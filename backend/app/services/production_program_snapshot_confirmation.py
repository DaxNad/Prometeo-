from __future__ import annotations

from collections.abc import Mapping
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

from app.domain.authority_roles import (
    ALLOWED_AUTHORITY_ROLES,
    normalize_authority_role,
)
from app.domain.production_program_snapshot_registry import (
    ProductionProgramSnapshotRegistry,
    ProductionProgramSnapshotRegistryError,
)
from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


@dataclass(frozen=True)
class ProductionProgramSnapshotConfirmationResult:
    ok: bool
    error_code: str | None = None
    record: dict[str, Any] | None = None
    write_performed: bool = False

    def as_dict(self) -> dict[str, Any]:
        record = copy.deepcopy(self.record) if self.record is not None else {}
        return {
            "ok": self.ok,
            "error_code": self.error_code,
            "status": record.get("status", "BLOCCATO"),
            "semantic_status": record.get("semantic_status", "BLOCCATO"),
            "requires_confirmation": not self.ok,
            "persisted": bool(record.get("persisted")),
            "write_performed": self.write_performed,
            "registry_id": record.get("registry_id"),
            "snapshot_id": record.get("snapshot_id"),
            "version": record.get("version"),
            "source": record.get("source"),
            "source_id": record.get("source_id"),
            "source_hash": record.get("source_hash"),
            "confirmed_by": record.get("confirmed_by"),
            "confirmed_at": record.get("confirmed_at"),
            "snapshot": record.get("snapshot"),
            "audit": record.get("audit"),
        }


def confirm_production_program_snapshot(
    *,
    registry: ProductionProgramSnapshotRegistry | None,
    source_id: str,
    source_hash: str,
    observed_text: str,
    snapshot_preview: Mapping[str, Any],
    actor_id: str,
    authority_role: str,
    confirmed_at: str,
    audit_note: str,
) -> ProductionProgramSnapshotConfirmationResult:
    normalized_actor = str(actor_id or "").strip()
    normalized_role = normalize_authority_role(authority_role)
    normalized_source_id = str(source_id or "").strip()
    normalized_source_hash = str(source_hash or "").strip().lower()
    normalized_text = str(observed_text or "")
    normalized_note = str(audit_note or "").strip()

    if not normalized_actor:
        return _blocked("ACTOR_ID_REQUIRED")
    if normalized_role not in ALLOWED_AUTHORITY_ROLES:
        return _blocked("UNAUTHORIZED_AUTHORITY_ROLE")
    try:
        normalized_confirmed_at = _normalize_timestamp(confirmed_at)
    except ValueError:
        return _blocked("INVALID_CONFIRMED_AT")
    if not normalized_source_id:
        return _blocked("SOURCE_ID_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{64}", normalized_source_hash):
        return _blocked("INVALID_SOURCE_HASH")
    if normalized_source_id != (
        f"production-program-image:sha256:{normalized_source_hash}"
    ):
        return _blocked("SOURCE_HASH_MISMATCH")
    if not normalized_text.strip():
        return _blocked("OBSERVED_TEXT_REQUIRED")
    if not normalized_note:
        return _blocked("AUDIT_NOTE_REQUIRED")
    if registry is None:
        return _blocked("REGISTRY_NOT_CONFIGURED")

    provided_preview = copy.deepcopy(dict(snapshot_preview))
    rebuilt_preview = build_production_program_snapshot_preview(
        normalized_text,
        source_id=normalized_source_id,
    )
    if provided_preview != rebuilt_preview:
        return _blocked("SNAPSHOT_PREVIEW_MISMATCH")
    if (
        provided_preview.get("ok") is not True
        or provided_preview.get("semantic_status") != "DA_VERIFICARE"
        or provided_preview.get("requires_confirmation") is not True
        or provided_preview.get("persisted") is not False
    ):
        return _blocked("PREVIEW_NOT_CONFIRMABLE")

    try:
        write_result = registry.confirm(
            source_id=normalized_source_id,
            source_hash=normalized_source_hash,
            snapshot=provided_preview,
            confirmed_by={
                "actor_id": normalized_actor,
                "authority_role": normalized_role,
            },
            confirmed_at=normalized_confirmed_at,
            audit_note=normalized_note,
        )
    except ProductionProgramSnapshotRegistryError as exc:
        return _blocked(exc.error_code)

    return ProductionProgramSnapshotConfirmationResult(
        ok=True,
        record=write_result.record,
        write_performed=write_result.write_performed,
    )


def _blocked(error_code: str) -> ProductionProgramSnapshotConfirmationResult:
    return ProductionProgramSnapshotConfirmationResult(
        ok=False,
        error_code=error_code,
    )


def _normalize_timestamp(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("timestamp required")
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return (
        parsed.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
