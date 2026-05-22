from __future__ import annotations

from app.services.controlled_import_preview import build_controlled_import_preview


EXPECTED_TOP_LEVEL_KEYS = {
    "ok",
    "capability",
    "write_mode",
    "preview_only",
    "required_human_confirmation",
    "risk_level",
    "risk_allowed_values",
    "errors",
    "warnings",
    "preview",
    "side_effects",
}

EXPECTED_PREVIEW_KEYS = {
    "order_id",
    "article_code",
    "quantity",
    "due_date",
    "priority",
    "route",
    "station",
    "note",
    "source_type",
}

EXPECTED_SIDE_EFFECT_KEYS = {
    "db_write",
    "smf_write",
    "planner_update",
    "file_write",
    "external_call",
    "ocr",
    "ai_runtime",
}

EXPECTED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "BLOCKED"}


def test_controlled_import_preview_output_schema_contract():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-SCHEMA-001",
            "article_code": "ART-SCHEMA-001",
            "quantity": 1,
            "route": ["ZAW1", "CP"],
            "source_type": "synthetic",
        }
    )

    assert set(result) == EXPECTED_TOP_LEVEL_KEYS
    assert set(result["preview"]) == EXPECTED_PREVIEW_KEYS
    assert set(result["side_effects"]) == EXPECTED_SIDE_EFFECT_KEYS
    assert set(result["risk_allowed_values"]) == EXPECTED_RISK_LEVELS
    assert result["risk_level"] in EXPECTED_RISK_LEVELS
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["preview_only"] is True
    assert result["required_human_confirmation"] is True
    assert all(value is False for value in result["side_effects"].values())


def test_controlled_import_preview_missing_required_fields_contract():
    result = build_controlled_import_preview({"source_type": "synthetic"})

    assert result["ok"] is False
    assert result["risk_level"] == "BLOCKED"
    assert "missing_required_field:order_id" in result["errors"]
    assert "missing_required_field:article_code" in result["errors"]
    assert "missing_required_field:quantity" in result["errors"]
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert result["required_human_confirmation"] is True
    assert all(value is False for value in result["side_effects"].values())


def test_controlled_import_preview_sensitive_input_schema_contract():
    result = build_controlled_import_preview(
        {
            "order_id": "DEMO-SCHEMA-002",
            "article_code": "ART-SCHEMA-002",
            "quantity": 1,
            "source_type": "synthetic",
            "note": "data/local_smf/SuperMegaFile_Master.xlsx",
        }
    )

    assert result["ok"] is False
    assert result["risk_level"] == "BLOCKED"
    assert result["preview"] == {}
    assert "sensitive_input_detected" in result["errors"]
    assert result["write_mode"] == "PREVIEW_ONLY"
    assert all(value is False for value in result["side_effects"].values())
