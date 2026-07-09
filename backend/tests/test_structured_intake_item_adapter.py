import inspect

import pytest

from app.services import structured_intake_item_adapter as adapter
from app.services.intake_destination_classifier import IntakeItem
from app.services.structured_intake_item_adapter import (
    ERROR_INVALID_PAYLOAD,
    ERROR_MISSING_FIELD_NAME,
    ERROR_MISSING_SOURCE_ID,
    StructuredIntakeAdapterStatus,
    build_intake_item,
)


def _payload(**overrides):
    payload = {
        "field_name": "operational_class",
        "value": "STANDARD",
        "source_id": "human:SYNTH01",
        "source_type": "human_operational_confirmation",
        "source_status": "SOURCE_FOUND",
        "semantic_status": "CERTO",
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "document_section": "CONFERME",
        "document_label": "STATO OPERATIVO",
        "context": {
            "article": "SYNTH01",
            "planner_eligible": True,
            "tl_confirmation_required": False,
        },
        "metadata": {
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        },
    }
    payload.update(overrides)
    return payload


def test_valid_mapping_builds_intake_item_without_mutating_input():
    payload = _payload()
    original_context = dict(payload["context"])
    original_metadata = dict(payload["metadata"])

    result = build_intake_item(payload)

    assert result.ok is True
    assert result.status == StructuredIntakeAdapterStatus.BUILT
    assert isinstance(result.item, IntakeItem)
    assert result.item.field_name == "operational_class"
    assert result.item.source_id == "human:SYNTH01"
    assert result.item.context == original_context
    assert result.item.metadata == original_metadata
    assert payload["context"] == original_context
    assert payload["metadata"] == original_metadata


@pytest.mark.parametrize("payload", [None, [], "invalid", object()])
def test_non_mapping_payload_is_rejected(payload):
    result = build_intake_item(payload)

    assert result.ok is False
    assert result.status == StructuredIntakeAdapterStatus.REJECTED
    assert result.item is None
    assert result.error_code == ERROR_INVALID_PAYLOAD


def test_missing_source_id_is_rejected():
    result = build_intake_item(_payload(source_id=""))

    assert result.ok is False
    assert result.item is None
    assert result.error_code == ERROR_MISSING_SOURCE_ID


def test_missing_field_name_is_rejected():
    result = build_intake_item(_payload(field_name=""))

    assert result.ok is False
    assert result.item is None
    assert result.error_code == ERROR_MISSING_FIELD_NAME


def test_unknown_top_level_fields_are_rejected():
    result = build_intake_item(_payload(unexpected="value"))

    assert result.ok is False
    assert result.item is None
    assert result.error_code == ERROR_INVALID_PAYLOAD


@pytest.mark.parametrize("field", ["context", "metadata"])
def test_context_and_metadata_must_be_mappings_or_none(field):
    result = build_intake_item(_payload(**{field: ["invalid"]}))

    assert result.ok is False
    assert result.item is None
    assert result.error_code == ERROR_INVALID_PAYLOAD


def test_adapter_preserves_false_zero_and_empty_value():
    for value in (False, 0, ""):
        result = build_intake_item(_payload(value=value))

        assert result.ok is True
        assert result.item.value == value


def test_adapter_has_no_classification_execution_batch_or_io():
    source = inspect.getsource(adapter)

    forbidden = (
        "classify_intake_destination",
        "plan_intake_placement",
        "execute_intake_placement",
        "orchestrate_intake_item",
        "open(",
        "write_text",
        "read_text",
        "json.load",
        "json.dump",
        "requests.",
        "httpx.",
        "for payload in",
    )
    assert all(token not in source for token in forbidden)


def test_adapter_does_not_hardcode_article_12514():
    assert "12514" not in inspect.getsource(adapter)
