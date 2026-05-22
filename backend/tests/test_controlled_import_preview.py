from __future__ import annotations

from app.services.controlled_import_preview import build_controlled_import_preview


def test_controlled_import_preview_builds_low_risk_preview_without_writes():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-001",
            "article_code": "ART-DEMO-001",
            "quantity": "12",
            "due_date": "2026-06-22",
            "priority": "ALTA",
            "station": "ZAW1",
            "route": ["ZAW1", "CP"],
            "note": "payload demo sanificato",
            "source_type": "synthetic",
        }
    )

    assert result["ok"] is True
    assert result["capability"] == "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1"
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["preview_only"] is True
    assert result["required_human_confirmation"] is True
    assert result["risk_level"] == "LOW"
    assert result["errors"] == []
    assert result["side_effects"] == {
        "db_write": False,
        "smf_write": False,
        "planner_update": False,
        "file_write": False,
        "external_call": False,
        "ocr": False,
        "ai_runtime": False,
    }

    preview = result["preview"]
    assert preview["order_id"] == "DEMO-001"
    assert preview["article_code"] == "ART-DEMO-001"
    assert preview["quantity"] == 12.0
    assert preview["due_date"] == "2026-06-22"
    assert preview["station"] == "ZAW-1"
    assert preview["route"] == ["ZAW-1", "CP"]


def test_controlled_import_preview_blocks_missing_required_fields():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-002",
            "source_type": "synthetic",
        }
    )

    assert result["ok"] is False
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["risk_level"] == "BLOCKED"
    assert "missing_required_field:article_code" in result["errors"]
    assert "missing_required_field:quantity" in result["errors"]
    assert result["side_effects"]["db_write"] is False
    assert result["side_effects"]["smf_write"] is False


def test_controlled_import_preview_blocks_sensitive_input_markers():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-003",
            "article_code": "ART-DEMO-003",
            "quantity": 5,
            "source_type": "synthetic",
            "note": "non usare " + chr(47) + "Users" + chr(47) + "test" + chr(47) + "specs_finitura" + chr(47) + "reale.pdf",
        }
    )

    assert result["ok"] is False
    assert result["risk_level"] == "BLOCKED"
    assert "sensitive_input_detected" in result["errors"]
    assert any(item.startswith("sensitive_marker:") for item in result["warnings"])
    assert result["preview"] == {}


def test_controlled_import_preview_marks_incomplete_safe_payload_medium_risk():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-004",
            "article_code": "ART-DEMO-004",
            "quantity": 3,
            "source_type": "demo",
        }
    )

    assert result["ok"] is True
    assert result["risk_level"] == "MEDIUM"
    assert result["preview"]["route"] == []
    assert result["required_human_confirmation"] is True


def test_controlled_import_preview_rejects_non_object_payload():
    result = build_controlled_import_preview(["not", "a", "dict"])  # type: ignore[arg-type]

    assert result["ok"] is False
    assert result["risk_level"] == "BLOCKED"
    assert result["errors"] == ["payload_must_be_object"]
    assert result["write_mode"] == "PREVIEW_ONLY"
