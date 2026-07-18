from __future__ import annotations

from collections.abc import Mapping
import copy
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REGISTRY_SCHEMA = "PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_V1"
REGISTRY_SOURCE = "production_program_snapshot_registry"
REGISTRY_PATH_ENV = "PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_PATH"


class ProductionProgramSnapshotRegistryError(RuntimeError):
    def __init__(self, error_code: str) -> None:
        super().__init__(error_code)
        self.error_code = error_code


@dataclass(frozen=True)
class ProductionProgramSnapshotWriteResult:
    record: dict[str, Any]
    write_performed: bool


class ProductionProgramSnapshotRegistry:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def confirm(
        self,
        *,
        source_id: str,
        source_hash: str,
        snapshot: Mapping[str, Any],
        confirmed_by: Mapping[str, str],
        confirmed_at: str,
        audit_note: str,
    ) -> ProductionProgramSnapshotWriteResult:
        document = self._read_document()
        registry_id = build_production_program_snapshot_registry_id(
            source_id=source_id,
            source_hash=source_hash,
        )
        normalized_snapshot = copy.deepcopy(dict(snapshot))
        content_hash = _canonical_hash(normalized_snapshot)

        snapshots = document["snapshots"]
        history = snapshots.get(registry_id)
        if history is not None and not isinstance(history, dict):
            raise ProductionProgramSnapshotRegistryError("INVALID_REGISTRY")

        versions = history.get("versions", []) if history else []
        if not isinstance(versions, list) or any(
            not isinstance(item, dict) for item in versions
        ):
            raise ProductionProgramSnapshotRegistryError("INVALID_REGISTRY")

        if versions and versions[-1].get("content_hash") == content_hash:
            return ProductionProgramSnapshotWriteResult(
                record=copy.deepcopy(versions[-1]),
                write_performed=False,
            )

        version = len(versions) + 1
        record = {
            "registry_id": registry_id,
            "snapshot_id": str(normalized_snapshot.get("snapshot_id") or ""),
            "version": version,
            "status": "CONFERMATO",
            "semantic_status": "CONFERMATO",
            "requires_confirmation": False,
            "persisted": True,
            "source": REGISTRY_SOURCE,
            "source_id": source_id,
            "source_hash": source_hash,
            "content_hash": content_hash,
            "confirmed_by": copy.deepcopy(dict(confirmed_by)),
            "confirmed_at": confirmed_at,
            "snapshot": normalized_snapshot,
            "audit": {
                "action": "HUMAN_EXPLICIT_CONFIRMATION",
                "actor_id": confirmed_by["actor_id"],
                "authority_role": confirmed_by["authority_role"],
                "confirmed_at": confirmed_at,
                "audit_note": audit_note,
                "source_id": source_id,
                "source_hash": source_hash,
                "content_hash": content_hash,
                "version": version,
            },
        }

        updated_document = copy.deepcopy(document)
        updated_document["snapshots"][registry_id] = {
            "registry_id": registry_id,
            "source_id": source_id,
            "source_hash": source_hash,
            "versions": [*copy.deepcopy(versions), record],
        }
        updated_document["updated_at"] = confirmed_at
        self._write_document_atomic(updated_document)

        readback = self.read_latest(registry_id)
        if readback is None or readback.get("content_hash") != content_hash:
            raise ProductionProgramSnapshotRegistryError(
                "WRITE_SUCCEEDED_READBACK_FAILED"
            )

        return ProductionProgramSnapshotWriteResult(
            record=readback,
            write_performed=True,
        )

    def read_latest(self, registry_id: str) -> dict[str, Any] | None:
        normalized_id = str(registry_id or "").strip()
        if not normalized_id.startswith(
            "production-program-verified:sha256:"
        ):
            return None

        document = self._read_document()
        history = document["snapshots"].get(normalized_id)
        if not isinstance(history, dict):
            return None
        versions = history.get("versions")
        if not isinstance(versions, list) or not versions:
            return None
        latest = versions[-1]
        return copy.deepcopy(latest) if isinstance(latest, dict) else None

    def _read_document(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_document()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProductionProgramSnapshotRegistryError(
                "INVALID_REGISTRY"
            ) from exc
        if (
            not isinstance(raw, dict)
            or raw.get("schema") != REGISTRY_SCHEMA
            or not isinstance(raw.get("snapshots"), dict)
        ):
            raise ProductionProgramSnapshotRegistryError("INVALID_REGISTRY")
        return raw

    def _write_document_atomic(self, document: dict[str, Any]) -> None:
        temporary_name: str | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(
                    document,
                    temporary,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            Path(temporary_name).replace(self.path)
        except OSError as exc:
            if temporary_name:
                try:
                    Path(temporary_name).unlink(missing_ok=True)
                except OSError:
                    pass
            raise ProductionProgramSnapshotRegistryError("WRITE_FAILED") from exc


def get_production_program_snapshot_registry(
) -> ProductionProgramSnapshotRegistry | None:
    configured_path = os.getenv(REGISTRY_PATH_ENV, "").strip()
    path = (
        Path(configured_path)
        if configured_path
        else _repo_root()
        / "data"
        / "production_program_snapshots"
        / "registry.json"
    )
    return ProductionProgramSnapshotRegistry(path)


def build_production_program_snapshot_registry_id(
    *,
    source_id: str,
    source_hash: str,
) -> str:
    digest = sha256(
        f"{source_id}\0{source_hash}".encode("utf-8")
    ).hexdigest()
    return f"production-program-verified:sha256:{digest}"


def _empty_document() -> dict[str, Any]:
    return {
        "schema": REGISTRY_SCHEMA,
        "updated_at": None,
        "snapshots": {},
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_hash(value: Mapping[str, Any]) -> str:
    serialized = json.dumps(
        dict(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return sha256(serialized.encode("utf-8")).hexdigest()
