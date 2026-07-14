from __future__ import annotations

import inspect

from app.services.production_program_snapshot_preview import (
    RECORD_DELIMITER,
    build_production_program_snapshot_preview,
)


VALID_INPUT = f"""\
PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50
DATA RICHIESTA CLIENTE: 2026-07-20
PRIORITÀ: ALTA
{RECORD_DELIMITER}
ORDINE: SYNTH-002
CODICE: ART-200
QTA: 25
DATA RICHIESTA CLIENTE: 2026-07-22
NOTA LIBERA NON CLASSIFICATA
"""


def test_valid_two_record_preview_is_deterministic_and_non_authoritative():
    first = build_production_program_snapshot_preview(VALID_INPUT)
    second = build_production_program_snapshot_preview(VALID_INPUT)

    assert first == second
    assert first["ok"] is True
    assert first["period"] == "2026-W30"
    assert first["source_type"] == "structured_text"
    assert first["source_status"] == "SOURCE_FOUND"
    assert first["snapshot_id"].startswith("production-program-snapshot:sha256:")
    assert first["source_id"].startswith("production-program-text:sha256:")
    assert len(first["orders"]) == 2
    assert first["semantic_status"] == "DA_VERIFICARE"
    assert first["confidence"] == "MEDIUM"
    assert first["requires_confirmation"] is True
    assert first["persisted"] is False
    assert first["writer_called"] is False
    assert first["planner_called"] is False
    assert first["pattern_learning_called"] is False

    first_order, second_order = first["orders"]
    assert first_order["order_id"] == "SYNTH-001"
    assert first_order["article_code"] == "ART-100"
    assert first_order["quantity"] == 50
    assert first_order["customer_requested_date"] == "2026-07-20"
    assert first_order["semantic_status"] == "DA_VERIFICARE"
    assert first_order["field_statuses"]["article_code"] == "DA_VERIFICARE"
    assert first_order["field_provenance"]["article_code"]["source_line"] == "CODICE: ART-100"

    assert second_order["order_id"] == "SYNTH-002"
    assert second_order["article_code"] == "ART-200"
    assert second_order["quantity"] == 25
    assert "NOTA LIBERA NON CLASSIFICATA" in second_order["unmatched_content"]


def test_missing_required_field_is_aggregated_without_defaulting_truth():
    text = f"""\
PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50
{RECORD_DELIMITER}
ORDINE: SYNTH-002
QTA: 25
"""

    result = build_production_program_snapshot_preview(text)

    assert result["ok"] is True
    assert result["semantic_status"] == "INCOMPLETO"
    assert result["confidence"] == "LOW"
    assert {"record_index": 2, "field": "article_code"} in result["missing_fields"]
    assert result["orders"][1]["article_code"] == ""
    assert result["orders"][1]["semantic_status"] == "INCOMPLETO"
    assert result["orders"][1]["field_statuses"]["article_code"] == "INCOMPLETO"


def test_generic_date_is_ambiguous_and_not_promoted_to_customer_requested_date():
    text = f"""\
PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50
DATA: 2026-07-20
{RECORD_DELIMITER}
ORDINE: SYNTH-002
CODICE: ART-200
QTA: 25
SCADENZA: 2026-07-22
"""

    result = build_production_program_snapshot_preview(text)

    assert result["ok"] is True
    assert result["confidence"] == "LOW"
    assert len(result["ambiguous_fields"]) == 2
    assert result["orders"][0]["customer_requested_date"] is None
    assert result["orders"][1]["customer_requested_date"] is None
    assert result["orders"][0]["ambiguous_fields"] == [
        {
            "field": "date_meaning",
            "raw_value": "2026-07-20",
            "source_line": "DATA: 2026-07-20",
            "observed_label": "DATA",
        }
    ]
    assert result["orders"][1]["ambiguous_fields"][0]["observed_label"] == "SCADENZA"


def test_non_separable_and_empty_inputs_fail_closed():
    no_delimiter = build_production_program_snapshot_preview(
        "ORDINE: SYNTH-001\nCODICE: ART-100\nQTA: 50"
    )
    empty = build_production_program_snapshot_preview("")

    for result, error in (
        (no_delimiter, "record_delimiter_required"),
        (empty, "empty_input"),
    ):
        assert result["ok"] is False
        assert result["source_status"] == "SOURCE_REJECTED"
        assert result["semantic_status"] == "BLOCCATO"
        assert result["orders"] == []
        assert result["discrepancies"] == [error]
        assert result["requires_confirmation"] is True
        assert result["persisted"] is False
        assert result["writer_called"] is False
        assert result["planner_called"] is False
        assert result["pattern_learning_called"] is False


def test_invalid_quantity_is_declared_as_missing_and_discrepant():
    text = f"""\
PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: non-numerica
{RECORD_DELIMITER}
ORDINE: SYNTH-002
CODICE: ART-200
QTA: 25
"""

    result = build_production_program_snapshot_preview(text)

    assert result["semantic_status"] == "INCOMPLETO"
    assert result["orders"][0]["quantity"] is None
    assert result["orders"][0]["discrepancies"] == ["quantity_not_numeric"]
    assert {"record_index": 1, "field": "quantity"} in result["missing_fields"]
    assert {"record_index": 1, "code": "quantity_not_numeric"} in result["discrepancies"]


def test_service_source_has_no_forbidden_integrations():
    from app.services import production_program_snapshot_preview as service

    source = inspect.getsource(service)
    required = (
        "parse_ocr_order_rows",
        "sha256",
        "RECORD_DELIMITER",
    )
    forbidden = (
        "SMFAdapter",
        "create_engine",
        "DATABASE_URL",
        "write_text",
        "write_bytes",
        "open(",
        "requests.",
        "httpx.",
        "UploadFile",
        "pandas",
        "read_excel",
        "tesseract",
        "pytesseract",
        "planner.",
        "agent_runtime",
        "pattern_learning.",
        "openai",
        "anthropic",
    )

    assert all(token in source for token in required)
    assert all(token not in source for token in forbidden)
