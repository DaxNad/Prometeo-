from __future__ import annotations

from datetime import datetime

from app.services.controlled_import_audit import build_controlled_import_audit_dry_run
from app.services.controlled_import_preview import build_controlled_import_preview


def test_controlled_import_audit_dry_run_records_preview_evaluation_without_writes():
    preview = build_controlled_import_preview(
        {
            "order_id": "DEMO-AUDIT-001",
            "article_code": "ART-AUDIT-001",
            "quantity": 2,
            "route": ["ZAW1", "CP"],
            "source_type": "synthetic",
        }
    )

    audit = build_controlled_import_audit_dry_run(preview)

    assert audit["ok"] is True
    assert audit["capability"] == "CONTROLLED_IMPORT_AUDIT_DRY_RUN_V1"
    assert audit["audit_mode"] == "DRY_RUN"
    assert audit["audit_event_type"] == "CONTROLLED_IMPORT_PREVIEW_EVALUATED"
    assert audit["source_capability"] == "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1"
    assert audit["preview_ok"] is True
    assert audit["risk_level"] == "LOW"
    assert audit["write_mode"] == "PREVIEW_ONLY"
    assert audit["human_confirmation_required"] is True
    assert audit["errors_count"] == 0
    assert audit["warnings_count"] == 0
    assert audit["apply_allowed"] is False
    assert all(value is False for value in audit["side_effects"].values())
    assert all(value is False for value in audit["persistence"].values())

    parsed_timestamp = datetime.fromisoformat(audit["timestamp_utc"])
    assert parsed_timestamp.tzinfo is not None


def test_controlled_import_audit_dry_run_records_blocked_preview():
    preview = build_controlled_import_preview(
        {
            "order_id": "DEMO-AUDIT-002",
            "article_code": "ART-AUDIT-002",
            "quantity": 1,
            "source_type": "synthetic",
            "note": "specs_finitura/reale.pdf",
        }
    )

    audit = build_controlled_import_audit_dry_run(preview)

    assert preview["ok"] is False
    assert audit["preview_ok"] is False
    assert audit["risk_level"] == "BLOCKED"
    assert audit["write_mode"] == "PREVIEW_ONLY"
    assert audit["human_confirmation_required"] is True
    assert audit["errors_count"] == 1
    assert audit["warnings_count"] >= 1
    assert audit["apply_allowed"] is False
    assert audit["persistence"]["db_write"] is False
    assert audit["persistence"]["file_write"] is False
    assert audit["persistence"]["smf_write"] is False
    assert audit["persistence"]["planner_update"] is False


def test_controlled_import_audit_dry_run_normalizes_missing_side_effects():
    audit = build_controlled_import_audit_dry_run(
        {
            "ok": False,
            "capability": "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1",
            "risk_level": "BLOCKED",
            "write_mode": "PREVIEW_ONLY",
            "required_human_confirmation": True,
            "errors": ["missing_required_field:quantity"],
            "warnings": [],
        }
    )

    assert audit["risk_level"] == "BLOCKED"
    assert audit["write_mode"] == "PREVIEW_ONLY"
    assert audit["human_confirmation_required"] is True
    assert all(value is False for value in audit["side_effects"].values())
    assert all(value is False for value in audit["persistence"].values())
