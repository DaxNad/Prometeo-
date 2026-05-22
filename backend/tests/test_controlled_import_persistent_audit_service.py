from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from app.services.controlled_import_persistent_audit import (
    ControlledImportPersistentAuditService,
)


class _FakeRepository:
    def __init__(self) -> None:
        self.records = []

    def record_event(self, payload):
        self.records.append(deepcopy(payload))
        return {
            "ok": True,
            "audit_event_id": payload["audit_event_id"],
            "persistence_status": payload["persistence_status"],
            "idempotent_replay": False,
            "error": None,
            "failure_reason": None,
            "apply_allowed": payload["apply_allowed"],
            "apply_executed": payload["apply_executed"],
        }


def _preview_result(risk_level: str = "LOW") -> dict:
    return {
        "ok": True,
        "capability": "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1",
        "risk_level": risk_level,
        "write_mode": "PREVIEW_ONLY",
        "required_human_confirmation": True,
        "preview": {
            "item_code": "DEMO-001",
            "route": ["CUT", "ASSEMBLY"],
        },
        "errors": [],
        "warnings": [],
        "side_effects": {
            "db_write": False,
            "smf_write": False,
            "planner_update": False,
            "file_write": False,
            "external_call": False,
            "ocr": False,
            "ai_runtime": False,
        },
    }


def _audit_dry_run(risk_level: str = "LOW") -> dict:
    return {
        "ok": True,
        "capability": "CONTROLLED_IMPORT_AUDIT_DRY_RUN_V1",
        "audit_mode": "DRY_RUN",
        "audit_event_type": "CONTROLLED_IMPORT_PREVIEW_EVALUATED",
        "timestamp_utc": "2026-05-22T10:00:00+00:00",
        "risk_level": risk_level,
        "write_mode": "PREVIEW_ONLY",
        "human_confirmation_required": True,
        "side_effects": {
            "db_write": False,
            "smf_write": False,
            "planner_update": False,
            "file_write": False,
            "external_call": False,
            "ocr": False,
            "ai_runtime": False,
        },
        "persistence": {
            "db_write": False,
            "file_write": False,
            "smf_write": False,
            "planner_update": False,
        },
        "apply_allowed": False,
    }


def test_persistent_audit_service_records_preview_audit_through_injected_repository():
    repo = _FakeRepository()
    service = ControlledImportPersistentAuditService(
        repository=repo,
        id_factory=lambda: "AUDIT-SERVICE-001",
        rollback_id_factory=lambda: "ROLLBACK-SERVICE-001",
        clock=lambda: datetime(2026, 5, 22, 10, 0, tzinfo=timezone.utc),
    )
    preview = _preview_result()
    original_preview = deepcopy(preview)

    result = service.persist_preview_audit(
        preview_result=preview,
        audit_dry_run=_audit_dry_run(),
        actor="tl-demo",
        source="controlled-import-preview",
        confirmation_token_hash="sha256:demo-hash",
    )

    assert result["ok"] is True
    assert result["audit_event_id"] == "AUDIT-SERVICE-001"
    assert result["rollback_id"] == "ROLLBACK-SERVICE-001"
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["apply_allowed"] is False
    assert result["apply_executed"] is False
    assert result["persistence_status"] == "RECORDED"
    assert preview == original_preview

    assert len(repo.records) == 1
    record = repo.records[0]
    assert record["actor"] == "tl-demo"
    assert record["source"] == "controlled-import-preview"
    assert record["confirmation_token_hash"] == "sha256:demo-hash"
    assert "confirmation_token" not in record
    assert record["risk_level"] == "LOW"
    assert record["write_mode"] == "PREVIEW_ONLY"
    assert record["strong_confirmation_status"] == "NOT_REQUIRED_FOR_PREVIEW"
    assert record["apply_allowed"] is False
    assert record["apply_executed"] is False
    assert record["before_state_hash"] is None
    assert record["after_state_hash"] is None
    assert record["preview_reference"].startswith("preview:sha256:")
    assert record["dry_run_reference"].startswith("dry-run:sha256:")
    assert record["side_effects_summary"]["db_write"] is False
    assert record["side_effects_summary"]["smf_write"] is False
    assert record["side_effects_summary"]["planner_update"] is False


def test_persistent_audit_service_rejects_missing_confirmation_token_hash():
    repo = _FakeRepository()
    service = ControlledImportPersistentAuditService(repository=repo)

    result = service.persist_preview_audit(
        preview_result=_preview_result(),
        audit_dry_run=_audit_dry_run(),
        actor="tl-demo",
        confirmation_token_hash="",
    )

    assert result["ok"] is False
    assert result["persistence_status"] == "BLOCKED"
    assert "confirmation_token_hash_required" in result["failure_reason"]
    assert repo.records == []


def test_persistent_audit_service_rejects_clear_confirmation_token():
    repo = _FakeRepository()
    service = ControlledImportPersistentAuditService(repository=repo)

    result = service.persist_preview_audit(
        preview_result=_preview_result(),
        audit_dry_run=_audit_dry_run(),
        actor="tl-demo",
        confirmation_token_hash="sha256:demo-hash",
        confirmation_token="CONFERMO IMPORT",
    )

    assert result["ok"] is False
    assert result["persistence_status"] == "BLOCKED"
    assert "clear_confirmation_token_forbidden" in result["failure_reason"]
    assert repo.records == []


def test_persistent_audit_service_rejects_clear_token_inside_input_payloads():
    repo = _FakeRepository()
    service = ControlledImportPersistentAuditService(repository=repo)
    preview = _preview_result()
    dry_run = _audit_dry_run()
    preview["confirmation_token"] = "raw-preview-token"
    dry_run["confirmation_token"] = "raw-dry-run-token"

    result = service.persist_preview_audit(
        preview_result=preview,
        audit_dry_run=dry_run,
        actor="tl-demo",
        confirmation_token_hash="sha256:demo-hash",
    )

    assert result["ok"] is False
    assert "preview_clear_confirmation_token_forbidden" in result["failure_reason"]
    assert "dry_run_clear_confirmation_token_forbidden" in result["failure_reason"]
    assert repo.records == []


def test_persistent_audit_service_rejects_blocked_risk_for_ordinary_preview_persistence():
    repo = _FakeRepository()
    service = ControlledImportPersistentAuditService(repository=repo)

    result = service.persist_preview_audit(
        preview_result=_preview_result(risk_level="BLOCKED"),
        audit_dry_run=_audit_dry_run(risk_level="BLOCKED"),
        actor="tl-demo",
        confirmation_token_hash="sha256:demo-hash",
    )

    assert result["ok"] is False
    assert result["persistence_status"] == "BLOCKED"
    assert "blocked_risk_not_persisted_for_preview" in result["failure_reason"]
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["apply_allowed"] is False
    assert result["apply_executed"] is False
    assert repo.records == []
