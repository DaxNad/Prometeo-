from __future__ import annotations

import base64
import copy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
import pytest

from app import api_smf
from app.api import api_planner
from app.api import tl_chat as tl_chat_api
from app.domain import production_program_snapshot_registry as registry_module
from app.api.production_program_image_ocr_acquisition import (
    get_production_program_ocr_adapter,
)
from app.ingest import ocr_ingest
from app.ingest.production_program_image_ocr_acquisition import (
    OCRTextExtractionResult,
)
from app.domain.production_program_snapshot_registry import (
    ProductionProgramSnapshotRegistry,
    ProductionProgramSnapshotRegistryError,
    get_production_program_snapshot_registry,
)
from app.main import app
from app.services.production_program_snapshot_confirmation import (
    confirm_production_program_snapshot,
)
from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


PNG = b"\x89PNG\r\n\x1a\nsynthetic-verified-snapshot"
OCR_TEXT = """PERIODO: 2026-W31
ordine: SYNTH-PP-001
codice: SYNTH-ARTICLE-001
qta: 12
data richiesta cliente: 2026-08-04
--- RECORD ---
ordine: SYNTH-PP-002
codice: SYNTH-ARTICLE-002
qta: 4
data richiesta cliente: 2026-08-05
"""
CONFIRMED_PERIOD_OCR_TEXT = """PERIODO: 2026-W30
ORDINE: ORD-001
Articolo 12069
Quantita richiesta: 24
Postazione: Banco assemblaggio
ORDINE: ORD-002
Articolo 12514
Quantita richiesta: 12
Postazione: Banco assemblaggio
"""
VERIFIED_MARKER = "PROMETEO_PROGRAM_VERIFIED_SNAPSHOT_V1"


class SyntheticOCRAdapter:
    def extract_text(
        self,
        image_bytes: bytes,
        *,
        media_type: str,
        source_id: str,
    ) -> OCRTextExtractionResult:
        assert image_bytes == PNG
        assert media_type == "image/png"
        assert source_id.startswith("production-program-image:sha256:")
        return OCRTextExtractionResult(
            ok=True,
            provider="synthetic-local",
            text=OCR_TEXT,
        )


class MemorySnapshotRegistry(ProductionProgramSnapshotRegistry):
    def __init__(self) -> None:
        super().__init__(Path("/synthetic/production-program-snapshots.json"))
        self.document: dict[str, Any] = {
            "schema": "PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_V1",
            "updated_at": None,
            "snapshots": {},
        }
        self.fail_writes = False

    def _read_document(self) -> dict[str, Any]:
        return copy.deepcopy(self.document)

    def _write_document_atomic(self, document: dict[str, Any]) -> None:
        if self.fail_writes:
            raise ProductionProgramSnapshotRegistryError("WRITE_FAILED")
        self.document = copy.deepcopy(document)

    def snapshot_bytes(self) -> bytes:
        return (
            json.dumps(self.document, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")


def _must_not_be_called(name: str):
    def guard(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError(f"{name} must not be called")

    return guard


def _confirmation_values(
    *,
    observed_text: str = OCR_TEXT,
) -> dict[str, Any]:
    source_hash = sha256(PNG).hexdigest()
    source_id = f"production-program-image:sha256:{source_hash}"
    return {
        "source_id": source_id,
        "source_hash": source_hash,
        "observed_text": observed_text,
        "snapshot_preview": build_production_program_snapshot_preview(
            observed_text,
            source_id=source_id,
        ),
        "actor_id": "synthetic-team-leader",
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "confirmed_at": "2026-08-01T08:30:00Z",
        "audit_note": "Synthetic production program confirmation.",
    }


def test_ocr_preview_requires_authorized_confirmation_before_persistent_tl_readback(
    monkeypatch,
) -> None:
    registry = MemorySnapshotRegistry()
    empty_registry = registry.snapshot_bytes()
    monkeypatch.setattr(
        ocr_ingest,
        "write_extracted_order_to_smf",
        _must_not_be_called("write_extracted_order_to_smf"),
    )
    monkeypatch.setattr(
        ocr_ingest,
        "write_extracted_orders_to_smf",
        _must_not_be_called("write_extracted_orders_to_smf"),
    )
    monkeypatch.setattr(
        api_planner,
        "planner_sequence",
        _must_not_be_called("planner_sequence"),
    )
    monkeypatch.setattr(
        api_smf,
        "_get_adapter",
        _must_not_be_called("SMFAdapter"),
    )
    app.dependency_overrides[get_production_program_ocr_adapter] = (
        lambda: SyntheticOCRAdapter()
    )
    app.dependency_overrides[get_production_program_snapshot_registry] = (
        lambda: registry
    )

    try:
        client = TestClient(app)
        acquisition_response = client.post(
            "/production-program/image-ocr/acquire",
            json={
                "image_base64": base64.b64encode(PNG).decode("ascii"),
            },
        )
        assert acquisition_response.status_code == 200
        acquisition = acquisition_response.json()
        assert acquisition["status"] == "PREVIEW_READY"
        assert acquisition["semantic_status"] == "DA_VERIFICARE"
        assert acquisition["requires_confirmation"] is True
        assert acquisition["persisted"] is False
        assert acquisition["snapshot_preview"]["semantic_status"] != "CERTO"
        assert registry.snapshot_bytes() == empty_registry

        confirmation_response = client.post(
            "/production-program-snapshot/confirm",
            json={
                "source_id": acquisition["source_id"],
                "source_hash": acquisition["source_hash"],
                "observed_text": acquisition["observed_text"],
                "snapshot_preview": acquisition["snapshot_preview"],
                "actor_id": "synthetic-team-leader",
                "authority_role": "RESPONSABILE_PRODUZIONE",
                "confirmed_at": "2026-08-01T08:30:00Z",
                "audit_note": "Synthetic production program confirmation.",
            },
        )

        assert confirmation_response.status_code == 200
        confirmation = confirmation_response.json()
        assert confirmation["ok"] is True
        assert confirmation["status"] == "CONFERMATO"
        assert confirmation["semantic_status"] == "CONFERMATO"
        assert confirmation["requires_confirmation"] is False
        assert confirmation["persisted"] is True
        assert confirmation["version"] == 1
        assert confirmation["source_id"] == acquisition["source_id"]
        assert confirmation["source_hash"] == acquisition["source_hash"]
        assert confirmation["confirmed_by"] == {
            "actor_id": "synthetic-team-leader",
            "authority_role": "RESPONSABILE_PRODUZIONE",
        }
        assert confirmation["confirmed_at"] == "2026-08-01T08:30:00Z"
        assert confirmation["snapshot_id"]
        assert confirmation["audit"] == {
            "action": "HUMAN_EXPLICIT_CONFIRMATION",
            "actor_id": "synthetic-team-leader",
            "authority_role": "RESPONSABILE_PRODUZIONE",
            "confirmed_at": "2026-08-01T08:30:00Z",
            "audit_note": "Synthetic production program confirmation.",
            "source_id": acquisition["source_id"],
            "source_hash": acquisition["source_hash"],
            "content_hash": confirmation["audit"]["content_hash"],
            "version": 1,
        }
        assert registry.snapshot_bytes() != empty_registry

        persisted_before_readback = registry.snapshot_bytes()
        monkeypatch.setattr(
            tl_chat_api,
            "build_production_program_snapshot_preview",
            _must_not_be_called(
                "build_production_program_snapshot_preview during readback"
            ),
        )
        tl_response = client.post(
            "/tl/chat",
            json={
                "question": (
                    f"{VERIFIED_MARKER}\n"
                    f"{confirmation['registry_id']}"
                ),
                "context": {},
            },
        )

        assert tl_response.status_code == 200
        tl_data = tl_response.json()
        assert tl_data["source"] == "production_program_snapshot_registry"
        assert tl_data["source_status"] == "SOURCE_FOUND"
        assert tl_data["semantic_status"] == "CONFERMATO"
        assert tl_data["confidence"] == "CONFERMATO"
        assert tl_data["requires_confirmation"] is False
        verified = tl_data["production_program_verified_snapshot"]
        assert verified["registry_id"] == confirmation["registry_id"]
        assert verified["snapshot_id"] == confirmation["snapshot_id"]
        assert verified["version"] == 1
        assert verified["source_id"] == acquisition["source_id"]
        assert verified["source_hash"] == acquisition["source_hash"]
        assert verified["confirmed_by"] == confirmation["confirmed_by"]
        assert verified["confirmed_at"] == confirmation["confirmed_at"]
        assert verified["status"] == "CONFERMATO"
        assert verified["snapshot"]["orders"][0]["order_id"] == "SYNTH-PP-001"
        assert registry.snapshot_bytes() == persisted_before_readback
    finally:
        app.dependency_overrides.pop(
            get_production_program_ocr_adapter,
            None,
        )
        app.dependency_overrides.pop(
            get_production_program_snapshot_registry,
            None,
        )


def test_tl_chat_reads_confirmed_production_program_by_period_without_mutation(
    monkeypatch,
) -> None:
    registry = MemorySnapshotRegistry()
    confirmation = confirm_production_program_snapshot(
        registry=registry,
        **_confirmation_values(observed_text=CONFIRMED_PERIOD_OCR_TEXT),
    )
    assert confirmation.ok is True
    assert confirmation.record is not None
    persisted_before_readback = registry.snapshot_bytes()

    monkeypatch.setattr(
        tl_chat_api,
        "_build_contract_response",
        _must_not_be_called("_build_contract_response"),
    )
    monkeypatch.setattr(
        ocr_ingest,
        "write_extracted_order_to_smf",
        _must_not_be_called("write_extracted_order_to_smf"),
    )
    monkeypatch.setattr(
        ocr_ingest,
        "write_extracted_orders_to_smf",
        _must_not_be_called("write_extracted_orders_to_smf"),
    )
    monkeypatch.setattr(
        api_planner,
        "planner_sequence",
        _must_not_be_called("planner_sequence"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "find_patterns_by_station",
        _must_not_be_called("find_patterns_by_station"),
    )
    app.dependency_overrides[get_production_program_snapshot_registry] = (
        lambda: registry
    )
    try:
        response = TestClient(app).post(
            "/tl/chat",
            json={
                "question": (
                    "Mostrami il programma produzione confermato 2026-W30"
                ),
                "context": {},
            },
        )
    finally:
        app.dependency_overrides.pop(
            get_production_program_snapshot_registry,
            None,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "production_program_snapshot_registry"
    assert data["source_status"] == "SOURCE_FOUND"
    assert data["semantic_status"] == "CONFERMATO"
    assert data["semantic_status"] != "CERTO"
    assert data["requires_confirmation"] is False
    assert "Periodo: 2026-W30" in data["answer"]
    assert "ORD-001" in data["answer"]
    assert "12069" in data["answer"]
    assert "24" in data["answer"]
    assert "Banco assemblaggio" in data["answer"]
    assert "ORD-002" in data["answer"]
    assert "12514" in data["answer"]
    assert "12" in data["answer"]

    verified = data["production_program_verified_snapshot"]
    assert verified["registry_id"] == confirmation.record["registry_id"]
    assert verified["version"] == 1
    assert verified["status"] == "CONFERMATO"
    assert verified["snapshot"]["period"] == "2026-W30"
    assert verified["snapshot"]["planner_called"] is False
    assert verified["snapshot"]["writer_called"] is False
    assert verified["snapshot"]["pattern_learning_called"] is False
    assert registry.snapshot_bytes() == persisted_before_readback


@pytest.mark.parametrize(
    ("overrides", "registry_present", "expected_error"),
    [
        ({"actor_id": ""}, True, "ACTOR_ID_REQUIRED"),
        (
            {"authority_role": "OPERATORE"},
            True,
            "UNAUTHORIZED_AUTHORITY_ROLE",
        ),
        ({"confirmed_at": "2026-08-01T08:30:00"}, True, "INVALID_CONFIRMED_AT"),
        ({"source_id": ""}, True, "SOURCE_ID_REQUIRED"),
        ({"source_hash": ""}, True, "INVALID_SOURCE_HASH"),
        ({"source_hash": "0" * 64}, True, "SOURCE_HASH_MISMATCH"),
        ({"observed_text": ""}, True, "OBSERVED_TEXT_REQUIRED"),
        ({"audit_note": ""}, True, "AUDIT_NOTE_REQUIRED"),
        ({}, False, "REGISTRY_NOT_CONFIGURED"),
    ],
)
def test_invalid_confirmation_inputs_are_blocked_before_persistence(
    overrides: dict[str, Any],
    registry_present: bool,
    expected_error: str,
) -> None:
    registry = MemorySnapshotRegistry()
    before = registry.snapshot_bytes()
    values = _confirmation_values()
    values.update(overrides)

    result = confirm_production_program_snapshot(
        registry=registry if registry_present else None,
        **values,
    )

    assert result.ok is False
    assert result.error_code == expected_error
    assert result.record is None
    assert result.write_performed is False
    assert registry.snapshot_bytes() == before


def test_preview_mismatch_is_blocked_without_persistence() -> None:
    registry = MemorySnapshotRegistry()
    values = _confirmation_values()
    values["snapshot_preview"] = {
        **values["snapshot_preview"],
        "semantic_status": "CERTO",
    }

    result = confirm_production_program_snapshot(
        registry=registry,
        **values,
    )

    assert result.error_code == "SNAPSHOT_PREVIEW_MISMATCH"
    assert registry.document["snapshots"] == {}


def test_same_confirmation_is_idempotent() -> None:
    registry = MemorySnapshotRegistry()
    values = _confirmation_values()

    first = confirm_production_program_snapshot(registry=registry, **values)
    after_first = registry.snapshot_bytes()
    second = confirm_production_program_snapshot(registry=registry, **values)

    assert first.ok is True
    assert first.write_performed is True
    assert second.ok is True
    assert second.write_performed is False
    assert second.record == first.record
    assert second.record["version"] == 1
    assert registry.snapshot_bytes() == after_first


def test_changed_confirmed_content_creates_a_new_version() -> None:
    registry = MemorySnapshotRegistry()
    first_values = _confirmation_values()
    changed_values = _confirmation_values(
        observed_text=OCR_TEXT.replace("qta: 12", "qta: 13")
    )

    first = confirm_production_program_snapshot(
        registry=registry,
        **first_values,
    )
    second = confirm_production_program_snapshot(
        registry=registry,
        **changed_values,
    )

    assert first.record["version"] == 1
    assert second.record["version"] == 2
    assert first.record["registry_id"] == second.record["registry_id"]
    history = registry.document["snapshots"][first.record["registry_id"]]
    assert [item["version"] for item in history["versions"]] == [1, 2]
    assert history["versions"][0]["snapshot"]["orders"][0]["quantity"] == 12
    assert history["versions"][1]["snapshot"]["orders"][0]["quantity"] == 13


def test_atomic_write_failure_preserves_previous_registry_state() -> None:
    registry = MemorySnapshotRegistry()
    before = registry.snapshot_bytes()
    registry.fail_writes = True

    result = confirm_production_program_snapshot(
        registry=registry,
        **_confirmation_values(),
    )

    assert result.ok is False
    assert result.error_code == "WRITE_FAILED"
    assert result.write_performed is False
    assert registry.snapshot_bytes() == before


def test_filesystem_registry_write_flushes_and_replaces_atomically(
    monkeypatch,
) -> None:
    events: list[tuple[str, Any]] = []

    class SyntheticTemporaryFile:
        name = "/synthetic/.production-program-snapshots.tmp"

        def __enter__(self):
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def write(self, value: str) -> int:
            events.append(("write", value))
            return len(value)

        def flush(self) -> None:
            events.append(("flush", None))

        def fileno(self) -> int:
            return 73

    def named_temporary_file(*args: Any, **kwargs: Any):
        events.append(("temporary", kwargs))
        return SyntheticTemporaryFile()

    def mkdir(path: Path, *args: Any, **kwargs: Any) -> None:
        events.append(("mkdir", path))

    def replace(path: Path, target: Path) -> Path:
        events.append(("replace", (path, target)))
        return target

    monkeypatch.setattr(
        registry_module.tempfile,
        "NamedTemporaryFile",
        named_temporary_file,
    )
    monkeypatch.setattr(registry_module.os, "fsync", lambda fd: events.append(("fsync", fd)))
    monkeypatch.setattr(Path, "mkdir", mkdir)
    monkeypatch.setattr(Path, "replace", replace)
    registry = ProductionProgramSnapshotRegistry(
        Path("/synthetic/production-program-snapshots.json")
    )

    registry._write_document_atomic(
        {
            "schema": "PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_V1",
            "updated_at": None,
            "snapshots": {},
        }
    )

    event_names = [name for name, _ in events]
    assert event_names.index("flush") < event_names.index("fsync")
    assert event_names.index("fsync") < event_names.index("replace")
    temporary_options = next(
        value for name, value in events if name == "temporary"
    )
    assert temporary_options["dir"] == Path("/synthetic")
    assert temporary_options["delete"] is False
    assert next(value for name, value in events if name == "fsync") == 73
    assert next(value for name, value in events if name == "replace") == (
        Path("/synthetic/.production-program-snapshots.tmp"),
        Path("/synthetic/production-program-snapshots.json"),
    )


def test_registry_uses_only_configured_or_controlled_local_path(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "PRODUCTION_PROGRAM_SNAPSHOT_REGISTRY_PATH",
        raising=False,
    )

    registry = get_production_program_snapshot_registry()

    assert registry is not None
    assert registry.path.parts[-3:] == (
        "data",
        "production_program_snapshots",
        "registry.json",
    )


def test_tl_chat_missing_snapshot_does_not_invent_data() -> None:
    registry = MemorySnapshotRegistry()
    app.dependency_overrides[get_production_program_snapshot_registry] = (
        lambda: registry
    )
    try:
        response = TestClient(app).post(
            "/tl/chat",
            json={
                "question": (
                    f"{VERIFIED_MARKER}\n"
                    "production-program-verified:sha256:"
                    + "0" * 64
                ),
                "context": {},
            },
        )
    finally:
        app.dependency_overrides.pop(
            get_production_program_snapshot_registry,
            None,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["source"] == "production_program_snapshot_registry"
    assert data["source_status"] == "SOURCE_MISSING"
    assert data["semantic_status"] == "MANCANTE"
    assert data["requires_confirmation"] is True
    assert data["missing_data"] == [
        "snapshot programma produzione persistito"
    ]
    assert "production_program_verified_snapshot" not in data
