from __future__ import annotations

import inspect

import pytest

from app.domain.authority_roles import (
    ALLOWED_AUTHORITY_ROLES,
    normalize_authority_role,
)
from app.domain.operation_normalization import (
    PRESSURE_TEST_NORMALIZATION_RULE,
    normalize_operation_value,
)
from app.services import article_operational_confirmation_service
from app.services import intake_destination_classifier
from app.services.intake_destination_classifier import (
    ERROR_INCOMPLETE_HUMAN_CONFIRMATION,
    ERROR_UNAUTHORIZED_AUTHORITY_ROLE,
    ERROR_UNCLASSIFIED,
    IntakeDestination,
    IntakeItem,
    classify_intake_destination,
    classify_intake_items,
)


def _item(**overrides):
    payload = {
        "field_name": "field",
        "value": "value",
        "source_id": "redteam:SYNTH",
        "source_type": "spec_intake_preview",
        "source_status": "PREVIEW_ONLY",
        "semantic_status": "DA_VERIFICARE",
    }
    payload.update(overrides)
    return IntakeItem(**payload)


@pytest.mark.parametrize(
    "item",
    [
        _item(field_name="tool", value="ATTREZZATURA PER COLLAUDO"),
        _item(document_section="ATTREZZATURE", value="ATTREZZATURA PER COLLAUDO"),
        _item(field_name="machine", value="MACCHINA DI CONTROLLO DIMENSIONALE"),
    ],
)
def test_tool_context_with_quality_words_stays_tools(item):
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.TOOLS
    assert result.destination != IntakeDestination.QUALITY_CONTROLS


@pytest.mark.parametrize(
    "value",
    [
        "VINCOLO: COLLAUDO SOLO DOPO MARCATURA",
        "NON ESEGUIRE IL COLLAUDO PRIMA DELL'ASSEMBLAGGIO",
        "RICHIEDE CONTROLLO DIMENSIONALE DOPO CRIMPATURA",
    ],
)
def test_constraint_markers_with_quality_words_stay_constraints(value):
    result = classify_intake_destination(_item(field_name="note", value=value))

    assert result.destination == IntakeDestination.CONSTRAINTS
    assert IntakeDestination.QUALITY_CONTROLS in result.candidate_destinations or result.destination == IntakeDestination.CONSTRAINTS


@pytest.mark.parametrize(
    "item",
    [
        _item(field_name="component", value="COMPONENTE PER PROVA PRESSIONE"),
        _item(document_section="COMPONENTI", value="COMPONENTE PER PROVA PRESSIONE"),
        _item(value={"value": "KIT COLLAUDO 468922", "type": "component"}),
    ],
)
def test_component_context_with_quality_words_stays_components(item):
    result = classify_intake_destination(item)

    assert result.destination == IntakeDestination.COMPONENTS
    assert result.destination not in {IntakeDestination.TOOLS, IntakeDestination.QUALITY_CONTROLS}


@pytest.mark.parametrize(
    ("value", "expected_normalized"),
    [
        ("CONTROLLO DIMENSIONALE 100%", "CONTROLLO DIMENSIONALE 100%"),
        ("COLLAUDO VISIVO 100%", "COLLAUDO VISIVO 100%"),
        ("COLLAUDO A PRESSIONE", "COLLAUDO A PRESSIONE VERTICALE"),
        ("COLLAUDO A PRESSIONE:", "COLLAUDO A PRESSIONE VERTICALE"),
        ("collaudo a pressione", "COLLAUDO A PRESSIONE VERTICALE"),
        ("  COLLAUDO   A   PRESSIONE  ", "COLLAUDO A PRESSIONE VERTICALE"),
    ],
)
def test_real_quality_controls_and_shared_normalization(value, expected_normalized):
    result = classify_intake_destination(_item(field_name="operation", value=value))

    assert result.destination == IntakeDestination.QUALITY_CONTROLS
    assert result.normalized_value == expected_normalized
    assert result.original_value == value


def test_quality_control_in_operations_keeps_route_context_but_selects_quality():
    result = classify_intake_destination(
        _item(
            field_name="operation",
            value="ESEGUIRE COLLAUDO A PRESSIONE VERTICALE",
            document_section="OPERAZIONI",
        )
    )

    assert result.destination == IntakeDestination.QUALITY_CONTROLS
    assert "DOCUMENT_SECTION_OPERATIONS" in result.matched_rules
    assert "QUALITY_OPERATION_EXACT_MATCH" in result.matched_rules


def test_machine_crimp_zaw_in_operations_stays_route_not_tools():
    result = classify_intake_destination(
        _item(value="MACCHINA CRIMP RING ZAW", document_section="OPERAZIONI")
    )

    assert result.destination == IntakeDestination.ROUTE
    assert result.destination != IntakeDestination.TOOLS


@pytest.mark.parametrize(
    "value",
    [
        "NOTA: COLLAUDO ESEGUITO IERI",
        "VA BENE IL COLLAUDO",
        "PRESSIONE",
    ],
)
def test_quality_words_without_definition_or_authority_are_not_quality(value):
    result = classify_intake_destination(_item(field_name="note", value=value))

    assert result.destination is None
    assert result.error_code == ERROR_UNCLASSIFIED
    assert result.requires_review is True


def test_control_isolated_requires_review_not_deterministic_quality():
    result = classify_intake_destination(_item(field_name="note", value="CONTROLLO"))

    assert result.destination is None
    assert result.error_code == ERROR_UNCLASSIFIED


def _complete_confirmation(**overrides):
    payload = {
        "field_name": "operational_class",
        "value": "STANDARD",
        "source_id": "human:SYNTH",
        "source_type": "human_operational_confirmation",
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "context": {"article": "SYNTH01"},
        "metadata": {
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        },
    }
    payload.update(overrides)
    return IntakeItem(**payload)


def test_complete_human_confirmation_is_classified():
    result = classify_intake_destination(_complete_confirmation())

    assert result.destination == IntakeDestination.HUMAN_CONFIRMATIONS
    assert result.requires_review is False


@pytest.mark.parametrize(
    "item",
    [
        _complete_confirmation(authority_role=None),
        _complete_confirmation(context={}),
        _complete_confirmation(value="va bene", field_name="", metadata={"confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION"}),
        _item(source_type="human_operational_confirmation", value="va bene"),
    ],
)
def test_incomplete_human_confirmation_requires_review(item):
    result = classify_intake_destination(item)

    assert result.destination is None
    assert result.error_code == ERROR_INCOMPLETE_HUMAN_CONFIRMATION
    assert result.candidate_destinations == (IntakeDestination.HUMAN_CONFIRMATIONS,)


def test_unauthorized_authority_role_is_invalid():
    result = classify_intake_destination(_complete_confirmation(authority_role="TL"))

    assert result.ok is False
    assert result.error_code == ERROR_UNAUTHORIZED_AUTHORITY_ROLE


@pytest.mark.parametrize(
    "value",
    [
        "NON USARE — REVISIONE PRECEDENTE",
        "NON USARE - REVISIONE PRECEDENTE",
        "NON USARE/REVISIONE PRECEDENTE",
        "NON USARE (REVISIONE PRECEDENTE)",
        "NON USARE L'ARTICOLO CON REVISIONE PRECEDENTE",
    ],
)
def test_unicode_and_punctuation_preserve_constraint_classification(value):
    result = classify_intake_destination(_item(field_name="note", value=value))

    assert result.destination == IntakeDestination.CONSTRAINTS


def test_matched_rules_and_candidate_destinations_are_deterministic():
    item = _item(
        value="CRT004",
        document_section="COMPONENTI",
        document_label="ATTREZZATURE",
    )

    first = classify_intake_destination(item)
    second = classify_intake_destination(item)

    assert first.matched_rules == second.matched_rules
    assert first.candidate_destinations == second.candidate_destinations
    assert first.candidate_destinations == (
        IntakeDestination.COMPONENTS,
        IntakeDestination.TOOLS,
    )


def test_operation_normalization_domain_module_is_deterministic_and_preserves_original():
    result = normalize_operation_value("  collaudo   a pressione  ")

    assert result.original_value == "  collaudo   a pressione  "
    assert result.normalized_value == "COLLAUDO A PRESSIONE VERTICALE"
    assert result.applied_rules == (
        "VALUE_TRIM",
        "VALUE_SPACES_COLLAPSED",
        PRESSURE_TEST_NORMALIZATION_RULE,
    )
    assert normalize_operation_value("LAVAGGIO").normalized_value == "LAVAGGIO"


def test_authority_roles_domain_module_is_shared_and_governed():
    assert normalize_authority_role(" responsabile produzione ") == "RESPONSABILE_PRODUZIONE"
    assert "RESPONSABILE_PRODUZIONE" in ALLOWED_AUTHORITY_ROLES
    assert normalize_authority_role("TL") not in ALLOWED_AUTHORITY_ROLES


def test_classifier_does_not_import_confirmation_service_for_authority_roles():
    source = inspect.getsource(intake_destination_classifier)

    assert "article_operational_confirmation_service import ALLOWED_AUTHORITY_ROLES" not in source


def test_confirmation_service_uses_shared_authority_roles():
    source = inspect.getsource(article_operational_confirmation_service)

    assert "from app.domain.authority_roles import" in source
    assert 'ALLOWED_AUTHORITY_ROLES = frozenset({"RESPONSABILE_PRODUZIONE"})' not in source


def test_distinct_sources_remain_distinct_in_red_team_batch():
    items = [
        _item(field_name="operation", value="COLLAUDO VISIVO 100%", source_id="src:A"),
        _item(field_name="operation", value="COLLAUDO VISIVO 100%", source_id="src:B"),
    ]

    results = classify_intake_items(items)

    assert [result.source_id for result in results] == ["src:A", "src:B"]
    assert all(result.destination == IntakeDestination.QUALITY_CONTROLS for result in results)


def test_large_batch_still_preserves_order_without_deduplication():
    items = [
        _item(field_name="operation", value="ASSEMBLAGGIO", source_id=f"batch:{idx}")
        for idx in range(1000)
    ]

    results = classify_intake_items(items)

    assert len(results) == 1000
    assert [result.source_id for result in results[:3]] == ["batch:0", "batch:1", "batch:2"]
    assert [result.source_id for result in results[-3:]] == ["batch:997", "batch:998", "batch:999"]


def test_no_hardcode_12514_in_classifier_runtime():
    source = inspect.getsource(intake_destination_classifier)

    assert "12514" not in source
