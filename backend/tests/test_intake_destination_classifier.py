from __future__ import annotations

import copy

import pytest

from app.services.intake_destination_classifier import (
    ERROR_AMBIGUOUS_MATCH,
    ERROR_CONFLICTING_RULES,
    ERROR_INVALID_INPUT,
    ERROR_INVALID_SCALAR_INPUT,
    ERROR_MISSING_SOURCE_ID,
    ERROR_UNAUTHORIZED_AUTHORITY_ROLE,
    ERROR_UNCLASSIFIED,
    ERROR_UNSUPPORTED_VALUE_TYPE,
    IntakeDestination,
    IntakeItem,
    classify_intake_destination,
    classify_intake_items,
)


def _item(**overrides):
    payload = {
        "field_name": "field",
        "value": "value",
        "source_id": "source:SYNTH",
        "source_type": "spec_intake_preview",
        "source_status": "PREVIEW_ONLY",
        "semantic_status": "DA_VERIFICARE",
    }
    payload.update(overrides)
    return IntakeItem(**payload)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("article", "SYNTH01"),
        ("disegno", "DRW-01"),
        ("rev", "A"),
        ("descrizione", "Articolo sintetico"),
        ("codice_cliente", "CLI-01"),
    ],
)
def test_article_fields_are_classified_as_article(field_name, value):
    result = classify_intake_destination(_item(field_name=field_name, value=value))

    assert result.ok is True
    assert result.destination == IntakeDestination.ARTICLE
    assert result.original_value == value
    assert "ARTICLE_FIELD_ALIAS" in result.matched_rules


@pytest.mark.parametrize("operation", ["LAVAGGIO", "ASSEMBLAGGIO", "INSERIMENTO GUAINA"])
def test_route_operations_are_classified_as_route(operation):
    result = classify_intake_destination(
        _item(field_name="operation", value=operation, document_section="OPERAZIONI")
    )

    assert result.destination == IntakeDestination.ROUTE
    assert result.classification_code == "ROUTE_FIELD_ALIAS"
    assert "DOCUMENT_SECTION_OPERATIONS" in result.matched_rules


def test_batch_preserves_operation_order():
    items = [
        _item(field_name="operation", value="LAVAGGIO", source_id="src:1"),
        _item(field_name="operation", value="ASSEMBLAGGIO", source_id="src:2"),
        _item(field_name="operation", value="INSERIMENTO GUAINA", source_id="src:3"),
    ]

    results = classify_intake_items(items)

    assert [result.source_id for result in results] == ["src:1", "src:2", "src:3"]
    assert [result.destination for result in results] == [
        IntakeDestination.ROUTE,
        IntakeDestination.ROUTE,
        IntakeDestination.ROUTE,
    ]


@pytest.mark.parametrize(
    "item",
    [
        _item(field_name="component_code", value="468922"),
        _item(field_name="bom_item", value={"code": "468796", "description": "Tubo"}),
        _item(field_name="field", value="468796", document_section="COMPONENTI"),
    ],
)
def test_components_require_declared_component_context(item):
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.COMPONENTS
    assert result.original_value == item.value


def test_numeric_code_without_component_evidence_is_not_tool_or_component():
    result = classify_intake_destination(_item(field_name="field", value="468796"))

    assert result.destination is None
    assert result.error_code == ERROR_UNCLASSIFIED
    assert result.requires_review is True


@pytest.mark.parametrize(
    "item",
    [
        _item(field_name="field", value={"code": "CRT004", "type": "tooling"}),
        _item(field_name="field", value={"code": "CRM004", "type": "tooling"}),
        _item(field_name="machine", value="MACCHINA ZAW"),
        _item(field_name="dima", value="DIMA CAD"),
    ],
)
def test_tools_are_classified_with_declared_tool_context(item):
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.TOOLS


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("COLLAUDO VISIVO 100%", "COLLAUDO VISIVO 100%"),
        ("COLLAUDO A PRESSIONE", "COLLAUDO A PRESSIONE VERTICALE"),
        ("COLLAUDO A PRESSIONE VERTICALE", "COLLAUDO A PRESSIONE VERTICALE"),
        ("CONTROLLO DIMENSIONALE CAD", "CONTROLLO DIMENSIONALE CAD"),
    ],
)
def test_quality_controls_include_confirmed_pressure_test_normalization(value, expected):
    result = classify_intake_destination(_item(field_name="operation", value=value))

    assert result.destination == IntakeDestination.QUALITY_CONTROLS
    assert result.normalized_value == expected
    assert result.original_value == value


@pytest.mark.parametrize(
    "value",
    [
        "richiede macchina ZAW",
        "non usare revisione precedente",
        "solo con clip",
    ],
)
def test_constraints_are_classified_from_operational_constraint_terms(value):
    result = classify_intake_destination(_item(field_name="note", value=value))

    assert result.destination == IntakeDestination.CONSTRAINTS


def test_descriptive_note_is_not_a_constraint_without_operational_effect():
    result = classify_intake_destination(_item(field_name="note", value="nota descrittiva per audit"))

    assert result.destination is None
    assert result.error_code == ERROR_UNCLASSIFIED


@pytest.mark.parametrize(
    "item",
    [
        _item(
            field_name="status",
            value="STANDARD",
            authority_role="RESPONSABILE_PRODUZIONE",
            context={"article": "SYNTH01"},
            metadata={
                "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
                "audit_note": "Conferma operativa sintetica.",
            },
        ),
        _item(
            field_name="status",
            value="STANDARD",
            source_type="human_operational_confirmation",
            authority_role="RESPONSABILE_PRODUZIONE",
            context={"article": "SYNTH01"},
            metadata={
                "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
                "audit_note": "Conferma operativa sintetica.",
            },
        ),
        _item(
            field_name="status",
            value={"confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION", "value": "STANDARD"},
            authority_role="RESPONSABILE_PRODUZIONE",
            context={"article": "SYNTH01"},
            metadata={"audit_note": "Conferma operativa sintetica."},
        ),
    ],
)
def test_structured_human_confirmations_are_classified(item):
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.HUMAN_CONFIRMATIONS
    assert "STRUCTURED_HUMAN_CONFIRMATION" in result.matched_rules


def test_generic_confirmation_phrase_without_authority_is_not_classified():
    result = classify_intake_destination(_item(field_name="note", value="va bene"))

    assert result.destination is None
    assert result.error_code == ERROR_UNCLASSIFIED


def test_operation_tool_ambiguity_uses_context_for_route():
    result = classify_intake_destination(
        _item(
            field_name="operation",
            value="MACCHINA CRIMP RING ZAW",
            document_section="OPERAZIONI",
        )
    )

    assert result.destination == IntakeDestination.ROUTE


def test_operation_tool_ambiguity_uses_declared_tool_type():
    result = classify_intake_destination(
        _item(
            field_name="field",
            value={"value": "MACCHINA CRIMP RING ZAW", "type": "tooling"},
        )
    )

    assert result.destination == IntakeDestination.TOOLS


def test_operation_tool_ambiguity_requires_review_without_context():
    result = classify_intake_destination(
        _item(field_name="field", value="MACCHINA CRIMP RING ZAW")
    )

    assert result.destination is None
    assert result.classification_code == "AMBIGUOUS_OPERATION_OR_TOOL"
    assert result.error_code == ERROR_AMBIGUOUS_MATCH
    assert result.candidate_destinations == (
        IntakeDestination.ROUTE,
        IntakeDestination.TOOLS,
    )


def test_conflicting_strong_rules_at_same_priority_require_review():
    result = classify_intake_destination(
        _item(
            field_name="field",
            value="CRT004",
            document_section="COMPONENTI",
            document_label="ATTREZZATURE",
        )
    )

    assert result.destination is None
    assert result.error_code == ERROR_CONFLICTING_RULES
    assert set(result.matched_rules) >= {"DOCUMENT_SECTION_COMPONENTS", "DOCUMENT_LABEL_TOOLS"}
    assert result.candidate_destinations == (
        IntakeDestination.COMPONENTS,
        IntakeDestination.TOOLS,
    )


@pytest.mark.parametrize(
    ("item", "error_code"),
    [
        (None, ERROR_INVALID_INPUT),
        (_item(field_name="", value="", source_id="source:empty"), ERROR_INVALID_INPUT),
        (_item(value=["LAVAGGIO"]), ERROR_INVALID_SCALAR_INPUT),
        (_item(source_id=""), ERROR_MISSING_SOURCE_ID),
        (_item(value=object()), ERROR_UNSUPPORTED_VALUE_TYPE),
        (_item(authority_role="TL"), ERROR_UNAUTHORIZED_AUTHORITY_ROLE),
    ],
)
def test_invalid_inputs_return_structured_errors(item, error_code):
    result = classify_intake_destination(item)  # type: ignore[arg-type]

    assert result.ok is False
    assert result.error_code == error_code
    assert result.requires_review is True


def test_batch_returns_one_result_per_item_and_does_not_stop_on_error():
    items = [
        _item(field_name="operation", value="LAVAGGIO", source_id="src:ok1"),
        _item(value=["invalid"], source_id="src:bad"),
        _item(field_name="machine", value="ZAW", source_id="src:ok2"),
    ]

    results = classify_intake_items(items)

    assert [result.source_id for result in results] == ["src:ok1", "src:bad", "src:ok2"]
    assert [result.ok for result in results] == [True, False, True]
    assert results[1].error_code == ERROR_INVALID_SCALAR_INPUT


def test_classification_is_deterministic_for_same_input():
    item = _item(
        field_name=" Operation ",
        value="  collaudo   a pressione  ",
        source_id="src:deterministic",
    )

    first = classify_intake_destination(item)
    second = classify_intake_destination(item)

    assert first == second
    assert first.normalized_field_name == "operation"
    assert first.normalized_value == "COLLAUDO A PRESSIONE VERTICALE"


def test_input_context_metadata_and_source_lists_are_not_mutated():
    context = {"article": "SYNTH01", "operation_index": 8}
    metadata = {"type": "tooling", "labels": ["fixture"]}
    value = {"value": "MACCHINA CRIMP RING ZAW", "type": "tooling"}
    before = (copy.deepcopy(context), copy.deepcopy(metadata), copy.deepcopy(value))

    item = _item(field_name="field", value=value, context=context, metadata=metadata)
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.TOOLS
    assert (context, metadata, value) == before


def test_identical_values_from_different_sources_remain_distinct():
    items = [
        _item(field_name="operation", value="LAVAGGIO", source_id="src:A"),
        _item(field_name="operation", value="LAVAGGIO", source_id="src:B"),
    ]

    results = classify_intake_items(items)

    assert len(results) == 2
    assert [result.source_id for result in results] == ["src:A", "src:B"]
    assert all(result.destination == IntakeDestination.ROUTE for result in results)


def test_large_batch_preserves_order_without_deduplication():
    items = [
        _item(field_name="operation", value="ASSEMBLAGGIO", source_id=f"src:{idx}")
        for idx in range(1000)
    ]

    results = classify_intake_items(items)

    assert len(results) == 1000
    assert [result.source_id for result in results[:3]] == ["src:0", "src:1", "src:2"]
    assert [result.source_id for result in results[-3:]] == ["src:997", "src:998", "src:999"]
    assert all(result.destination == IntakeDestination.ROUTE for result in results)


def test_no_runtime_article_code_special_case_for_12514():
    result = classify_intake_destination(
        _item(field_name="article", value="12514", source_id="src:not-special")
    )

    assert result.destination == IntakeDestination.ARTICLE
    assert "12514" not in "".join(result.matched_rules)
