from __future__ import annotations

import inspect

import pytest

from app.ingest import article_specification_parser as parser
from app.services.intake_destination_classifier import (
    IntakeDestination,
    classify_intake_destination,
)
from app.services.structured_intake_item_adapter import build_intake_item
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeStatus,
    process_structured_intake_payload,
)


@pytest.fixture
def photographed_12514_rows() -> list[str]:
    return [
        "ARTICOLO: 12514",
        "CODICE: 7056055000A0",
        "DISEGNO: A1675003603",
        "REV: 6",
        "OPERAZIONI",
        "LAVAGGIO",
        "MACCHINA CRIMP RING ZAW",
        "COLLAUDO A PRESSIONE",
        "COMPONENTI",
        "468922 GUAINA",
        "ATTREZZATURE",
        "CRT004 ATTREZZATURA",
    ]


def test_12514_fixture_builds_governed_payloads_for_existing_intake_pipeline(
    photographed_12514_rows,
):
    source_id = "photographed-spec:test-fixture:12514"

    result = parser.parse_article_specification_rows(
        photographed_12514_rows,
        source_id=source_id,
    )

    assert result.ok is True
    assert result.status == parser.ArticleSpecificationParseStatus.PARSED
    assert result.source_id == source_id
    assert result.unmatched_lines == ()
    assert result.payloads

    assert all(payload["source_id"] == source_id for payload in result.payloads)
    assert all(
        payload["source_type"] == "photographed_article_spec_text"
        for payload in result.payloads
    )
    assert all(payload["source_status"] == "SOURCE_FOUND" for payload in result.payloads)
    assert all(payload["semantic_status"] == "DA_VERIFICARE" for payload in result.payloads)
    assert all(
        payload["metadata"]["field_status"] == "DA_VERIFICARE"
        for payload in result.payloads
    )

    article_payload = next(
        payload for payload in result.payloads if payload["field_name"] == "article"
    )
    assert article_payload["value"] == "12514"
    assert article_payload["metadata"]["source_line"] == "ARTICOLO: 12514"
    assert article_payload["metadata"]["source_line_number"] == 1

    route_payloads = [
        payload for payload in result.payloads if payload["field_name"] == "operation"
    ]
    assert [payload["value"] for payload in route_payloads] == [
        "LAVAGGIO",
        "MACCHINA CRIMP RING ZAW",
        "COLLAUDO A PRESSIONE",
    ]
    assert all(
        payload["context"]["route_status"] == "DA_VERIFICARE"
        for payload in route_payloads
    )
    assert all(
        payload["metadata"]["route_evidence"] == "UNCONFIRMED_EXTRACTED_TEXT"
        for payload in route_payloads
    )
    assert route_payloads[0]["metadata"]["source_line_number"] == 6

    classifications = []
    for payload in result.payloads:
        adapter_result = build_intake_item(payload)
        assert adapter_result.ok is True
        assert adapter_result.item is not None
        classifications.append(classify_intake_destination(adapter_result.item))

        orchestration = process_structured_intake_payload(payload)
        assert orchestration.status == StructuredIntakeFacadeStatus.NOT_EXECUTED
        assert orchestration.writer_called is False

    assert {classification.destination for classification in classifications} == {
        IntakeDestination.ARTICLE,
        IntakeDestination.ROUTE,
        IntakeDestination.COMPONENTS,
        IntakeDestination.TOOLS,
        IntakeDestination.QUALITY_CONTROLS,
    }


def test_text_block_input_preserves_governed_field_status():
    result = parser.parse_article_specification_rows(
        "ARTICOLO: 99999\nOPERAZIONI\nLAVAGGIO",
        source_id="photographed-spec:test-fixture:99999",
    )

    assert result.ok is True
    assert [payload["field_name"] for payload in result.payloads] == [
        "article",
        "operation",
    ]
    assert all(payload["semantic_status"] == "DA_VERIFICARE" for payload in result.payloads)
    assert result.payloads[1]["context"]["route_status"] == "DA_VERIFICARE"


@pytest.mark.parametrize(
    ("rows", "source_id", "error_code"),
    [
        ([], "source:test", parser.ERROR_EMPTY_INPUT),
        (["ARTICOLO: 99999"], "", parser.ERROR_MISSING_SOURCE_ID),
        ([{"text": "ARTICOLO: 99999"}], "source:test", parser.ERROR_INVALID_INPUT),
    ],
)
def test_invalid_parser_input_is_rejected(rows, source_id, error_code):
    result = parser.parse_article_specification_rows(rows, source_id=source_id)

    assert result.ok is False
    assert result.status == parser.ArticleSpecificationParseStatus.REJECTED
    assert result.payloads == ()
    assert result.error_code == error_code


def test_parser_is_separate_pure_and_article_agnostic():
    source = inspect.getsource(parser)

    forbidden = (
        "ocr_parser",
        "parse_ocr_order_rows",
        "build_intake_item",
        "process_structured_intake_payload",
        "orchestrate_intake_item",
        "write_text",
        "json.dump",
        "open(",
        "requests.",
        "httpx.",
        "openai",
        "anthropic",
        "langchain",
        "12514",
        '"CERTO"',
    )
    assert all(token not in source for token in forbidden)
