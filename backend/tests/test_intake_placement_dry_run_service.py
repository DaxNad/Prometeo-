from __future__ import annotations

import builtins
import copy
import inspect
from pathlib import Path

import pytest

from app.services.intake_destination_classifier import (
    IntakeDestination,
    IntakeItem,
    classify_intake_destination,
)
from app.services.article_operational_confirmation_service import (
    confirm_article_operational_status,
)
from app.services.intake_placement_dry_run_service import (
    ERROR_CLASSIFICATION_SOURCE_MISMATCH,
    ERROR_CLASSIFICATION_VALUE_MISMATCH,
    ERROR_DESTINATION_MISSING,
    ERROR_DRY_RUN_REQUIRED,
    ERROR_INVALID_PLACEMENT_REQUEST,
    ERROR_INVALID_TARGET_PAYLOAD,
    ERROR_MISSING_REQUIRED_FIELDS,
    ERROR_TARGET_NOT_AVAILABLE,
    PLACEMENT_TARGETS,
    IntakePlacementDryRunRequest,
    PlacementDryRunStatus,
    PlacementOperation,
    plan_intake_placement,
    plan_intake_placements,
)
from app.services import intake_placement_dry_run_service as service


def _item(**overrides):
    payload = {
        "field_name": "operation",
        "value": "ASSEMBLAGGIO",
        "source_id": "source:SYNTH",
        "source_type": "spec_intake_preview",
        "source_status": "SOURCE_FOUND",
        "semantic_status": "CERTO",
        "context": {"article": "SYNTH01", "sequence": 1},
    }
    payload.update(overrides)
    return IntakeItem(**payload)


def _request(item: IntakeItem | None = None, **overrides):
    item = item or _item()
    classification = classify_intake_destination(item)
    payload = {"item": item, "classification": classification, "dry_run": True}
    payload.update(overrides)
    return IntakePlacementDryRunRequest(**payload)


def test_dry_run_false_is_rejected():
    result = plan_intake_placement(_request(dry_run=False))

    assert result.status == PlacementDryRunStatus.INVALID_PLACEMENT_REQUEST
    assert result.error_code == ERROR_DRY_RUN_REQUIRED


def test_source_mismatch_is_rejected():
    request = _request()
    mismatched = request.classification.__class__(
        **{**request.classification.__dict__, "source_id": "other"}
    )

    result = plan_intake_placement(_request(classification=mismatched))

    assert result.error_code == ERROR_CLASSIFICATION_SOURCE_MISMATCH


def test_value_mismatch_is_rejected():
    request = _request()
    mismatched = request.classification.__class__(
        **{**request.classification.__dict__, "original_value": "ALTRO"}
    )

    result = plan_intake_placement(_request(classification=mismatched))

    assert result.error_code == ERROR_CLASSIFICATION_VALUE_MISMATCH


def test_classification_requires_review_blocks_placement():
    item = _item(field_name="field", value="MACCHINA CRIMP RING ZAW")
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False
    assert result.matched_rules == ("WEAK_OPERATION_TOOL_AMBIGUITY",)


def test_destination_missing_is_rejected():
    request = _request()
    classification = request.classification.__class__(
        **{**request.classification.__dict__, "destination": None}
    )

    result = plan_intake_placement(_request(classification=classification))

    assert result.error_code == ERROR_DESTINATION_MISSING


def test_missing_source_id_is_invalid():
    item = _item(source_id="")
    classification = classify_intake_destination(item)
    result = plan_intake_placement(IntakePlacementDryRunRequest(item=item, classification=classification))

    assert result.error_code == ERROR_INVALID_PLACEMENT_REQUEST


def test_article_payload_preview_and_target_not_available():
    item = _item(field_name="drawing", value="DRW-01", context={"article": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.destination == IntakeDestination.ARTICLE
    assert result.domain_entity == "Article"
    assert result.target_repository is None
    assert result.target_service is None
    assert result.target_section == "article_metadata"
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert result.ready_for_persistence is False
    assert result.payload_preview["article"] == "SYNTH01"
    assert result.payload_preview["field_name"] == "drawing"
    assert result.source_status == "SOURCE_FOUND"


def test_article_id_present_does_not_imply_update():
    item = _item(field_name="drawing", value="DRW-01", context={"article": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.operation != PlacementOperation.UPDATE
    assert result.operation == PlacementOperation.NOT_AVAILABLE


def test_article_id_missing_does_not_imply_create():
    item = _item(field_name="drawing", value="DRW-01", context={})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert result.operation != PlacementOperation.CREATE
    assert result.operation == PlacementOperation.NOT_AVAILABLE


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("drawing", "DRW-01"),
        ("revision", "A"),
        ("description", "Tubo sagomato"),
        ("material", "PA12"),
        ("customer_code", "CUST-01"),
    ],
)
def test_complete_article_fields_remain_logical_target_not_available(field_name, value):
    item = _item(field_name=field_name, value=value, context={"article": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert result.ready_for_persistence is False
    assert result.payload_preview["article"] == "SYNTH01"
    assert result.payload_preview["field_name"] == field_name
    assert result.payload_preview["value"] == value


def test_article_preview_only_requires_review_not_ready():
    item = _item(
        field_name="revision",
        value="A",
        source_status="PREVIEW_ONLY",
        semantic_status="DA_VERIFICARE",
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False
    assert result.operation == PlacementOperation.NOT_AVAILABLE


def test_article_da_verificare_requires_review_not_ready():
    item = _item(
        field_name="revision",
        value="A",
        semantic_status="DA_VERIFICARE",
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False
    assert result.operation == PlacementOperation.NOT_AVAILABLE


@pytest.mark.parametrize(
    ("source_status", "expected_status"),
    [
        ("SOURCE_FORBIDDEN", PlacementDryRunStatus.SOURCE_NOT_AUTHORIZED),
        ("SOURCE_MISSING", PlacementDryRunStatus.BLOCKED),
    ],
)
def test_article_blocked_source_statuses_do_not_create_operations(source_status, expected_status):
    item = _item(
        field_name="drawing",
        value="DRW-01",
        source_status=source_status,
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == expected_status
    assert result.operation == PlacementOperation.NOT_AVAILABLE


def test_route_with_article_and_sequence_builds_plan_but_no_writer():
    item = _item(field_name="operation", value="LAVAGGIO", context={"article": "SYNTH01", "sequence": 2})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.domain_entity == "Route"
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert result.payload_preview["operation_name"] == "LAVAGGIO"
    assert result.payload_preview["sequence"] == 2


def test_route_missing_sequence_is_missing_required_fields():
    item = _item(field_name="operation", value="LAVAGGIO", context={"article": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert result.missing_fields == ("sequence",)


def test_route_does_not_invent_station():
    item = _item(field_name="operation", value="LAVAGGIO", context={"article": "SYNTH01", "sequence": 1})
    result = plan_intake_placement(_request(item))

    assert result.payload_preview["station"] is None


def test_component_with_quantity_builds_plan_but_no_writer():
    item = _item(
        field_name="component",
        value={"value": "468922", "type": "component"},
        context={"article": "SYNTH01", "quantity": 2},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.domain_entity == "ArticleComponentRelation"
    assert result.payload_preview["component_code"] == "468922"
    assert result.payload_preview["quantity"] == 2


def test_component_missing_quantity_does_not_assume_one():
    item = _item(
        field_name="component",
        value={"value": "468922", "type": "component"},
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert result.missing_fields == ("quantity",)
    assert result.payload_preview["quantity"] is None


def test_tool_builds_plan_without_creating_station():
    item = _item(field_name="machine", value="MACCHINA ZAW", context={"article": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.domain_entity == "ToolRequirement"
    assert result.payload_preview["tool_name"] == "MACCHINA ZAW"
    assert result.payload_preview["station"] is None


def test_quality_control_preserves_original_normalized_and_rules():
    item = _item(
        field_name="operation",
        value="COLLAUDO A PRESSIONE",
        context={"article": "SYNTH01", "operation_index": 8},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.domain_entity == "QualityControlRequirement"
    assert result.payload_preview["control_name"] == "COLLAUDO A PRESSIONE VERTICALE"
    assert result.payload_preview["source_value"] == "COLLAUDO A PRESSIONE"
    assert result.payload_preview["normalization_rules_applied"] == (
        "OPERATION_COLLAUDO_PRESSIONE_CONFIRMED_NORMALIZATION",
    )
    assert "not duplicated into Route" in result.warnings[0]


def test_quality_preview_only_is_review_required():
    item = _item(
        field_name="operation",
        value="COLLAUDO VISIVO 100%",
        source_status="PREVIEW_ONLY",
        semantic_status="DA_VERIFICARE",
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False


def test_constraint_with_subject_builds_plan_but_no_writer():
    item = _item(field_name="note", value="NON USARE REVISIONE PRECEDENTE", context={"subject": "SYNTH01"})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.domain_entity == "OperationalConstraint"
    assert result.payload_preview["constraint_text"] == "NON USARE REVISIONE PRECEDENTE"


def test_constraint_missing_subject_requires_review():
    item = _item(field_name="note", value="NON USARE REVISIONE PRECEDENTE", context={})
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.missing_fields == ("subject",)


def _human_item(**overrides):
    payload = {
        "field_name": "operational_class",
        "value": "STANDARD",
        "source_id": "human:SYNTH",
        "source_type": "human_operational_confirmation",
        "source_status": "SOURCE_FOUND",
        "semantic_status": "CERTO",
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "context": {"article": "SYNTH01"},
        "metadata": {
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
            "planner_eligible": True,
            "tl_confirmation_required": False,
        },
    }
    payload.update(overrides)
    return IntakeItem(**payload)


def test_incomplete_human_operational_status_is_missing_required_booleans():
    item = _human_item(
        metadata={
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        }
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert result.ready_for_persistence is False
    assert result.target_service == "confirm_article_operational_status"
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert result.missing_fields == ("planner_eligible", "tl_confirmation_required")


def test_complete_human_operational_status_targets_governed_service_without_calling_it():
    item = _human_item()
    result = plan_intake_placement(_request(item))

    writer_arguments = result.payload_preview["writer_arguments"]

    assert result.status == PlacementDryRunStatus.READY
    assert result.ready_for_persistence is True
    assert result.target_service == "confirm_article_operational_status"
    assert result.operation == PlacementOperation.APPEND
    assert writer_arguments["article"] == "SYNTH01"
    assert writer_arguments["operational_class"] == "STANDARD"
    assert writer_arguments["planner_eligible"] is True
    assert writer_arguments["tl_confirmation_required"] is False
    assert writer_arguments["authority_role"] == "RESPONSABILE_PRODUZIONE"
    assert writer_arguments["audit_note"] == "Conferma operativa esplicita."
    assert writer_arguments["confirmation_origin"] == "HUMAN_EXPLICIT_CONFIRMATION"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("planner_eligible", "true"),
        ("tl_confirmation_required", "false"),
    ],
)
def test_human_operational_status_rejects_string_booleans(field_name, value):
    item = _human_item(
        metadata={
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
            "planner_eligible": True,
            "tl_confirmation_required": False,
            field_name: value,
        }
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.INVALID_PLACEMENT_REQUEST
    assert result.ready_for_persistence is False
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert result.error_code == ERROR_INVALID_TARGET_PAYLOAD


@pytest.mark.parametrize("operational_class", ["STANDARD", "REFERENCE_ONLY"])
def test_operational_class_does_not_derive_required_booleans(operational_class):
    item = _human_item(
        value=operational_class,
        metadata={
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        },
    )
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert result.missing_fields == ("planner_eligible", "tl_confirmation_required")


def test_human_confirmation_for_other_field_has_no_governed_writer():
    item = _human_item(field_name="drawing", value="DRW-01")
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.TARGET_NOT_AVAILABLE
    assert result.target_service is None
    assert result.operation == PlacementOperation.NOT_AVAILABLE
    assert "writer_arguments" in result.payload_preview


def test_human_preview_source_is_review_required_without_append_operation():
    item = _human_item(source_status="PREVIEW_ONLY")
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False
    assert result.operation == PlacementOperation.NOT_AVAILABLE


def test_human_confirmation_without_authority_requires_review():
    item = _human_item(authority_role=None)
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.REVIEW_REQUIRED
    assert result.ready_for_persistence is False


@pytest.mark.parametrize(
    ("source_status", "semantic_status", "expected"),
    [
        ("PREVIEW_ONLY", "CERTO", PlacementDryRunStatus.REVIEW_REQUIRED),
        ("SOURCE_FOUND", "DA_VERIFICARE", PlacementDryRunStatus.REVIEW_REQUIRED),
        ("SOURCE_FOUND", "CERTO", PlacementDryRunStatus.TARGET_NOT_AVAILABLE),
        ("SOURCE_MISSING", "CERTO", PlacementDryRunStatus.BLOCKED),
        ("SOURCE_FORBIDDEN", "CERTO", PlacementDryRunStatus.SOURCE_NOT_AUTHORIZED),
        ("SOURCE_AUTHORIZED_BUT_UNAVAILABLE", "CERTO", PlacementDryRunStatus.BLOCKED),
    ],
)
def test_source_policy_matrix(source_status, semantic_status, expected):
    item = _item(
        field_name="drawing",
        value="DRW-01",
        source_status=source_status,
        semantic_status=semantic_status,
        context={"article": "SYNTH01"},
    )
    result = plan_intake_placement(_request(item))

    assert result.status == expected


def test_dry_run_does_not_call_known_writers(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("writer called")

    monkeypatch.setattr(Path, "write_text", fail)
    monkeypatch.setattr(builtins, "open", fail)
    monkeypatch.setattr(service, "plan_intake_placements", service.plan_intake_placements)

    monkeypatch.setattr(
        "app.services.article_operational_confirmation_service.confirm_article_operational_status",
        fail,
    )

    item = _human_item()
    result = plan_intake_placement(_request(item))

    assert result.status == PlacementDryRunStatus.READY


def test_service_source_has_no_write_calls_or_writer_imports():
    source = inspect.getsource(service)

    forbidden = ("write_text", "json.dump", ".replace(", "confirm_article_operational_status(")
    for token in forbidden:
        assert token not in source


def test_service_source_does_not_read_operational_registry_to_choose_operation():
    source = inspect.getsource(service)

    forbidden_readers = (
        "get_operational_registry_entry",
        "build_article_tl_summary",
        "load_article_operational_registry",
        "article_operational_summary",
        "resolve_article_profile",
        "get_article_profile",
        "get_article_metadata",
        "article_exists",
    )
    for token in forbidden_readers:
        assert token not in source


def test_service_source_does_not_call_article_writers():
    source = inspect.getsource(service)

    forbidden_writers = (
        "save_article",
        "update_article",
        "create_article",
        "ArticleRepository",
    )
    for token in forbidden_writers:
        assert token not in source


def test_determinism_for_identical_request():
    request = _request()

    assert plan_intake_placement(request) == plan_intake_placement(request)


def test_determinism_preserves_article_not_available_operation():
    request = _request(_item(field_name="drawing", value="DRW-01", context={"article": "SYNTH01"}))

    first = plan_intake_placement(request)
    second = plan_intake_placement(request)

    assert first == second
    assert first.operation == PlacementOperation.NOT_AVAILABLE


def test_determinism_preserves_human_confirmation_append_operation():
    request = _request(_human_item())

    first = plan_intake_placement(request)
    second = plan_intake_placement(request)

    assert first == second
    assert first.operation == PlacementOperation.APPEND


def test_request_item_classification_context_metadata_are_not_mutated():
    item = _item(context={"article": "SYNTH01", "sequence": 1}, metadata={"tag": ["x"]})
    classification = classify_intake_destination(item)
    request = IntakePlacementDryRunRequest(item=item, classification=classification)
    before = copy.deepcopy((item.context, item.metadata, classification))

    plan_intake_placement(request)

    assert (item.context, item.metadata, classification) == before


def test_batch_preserves_order_errors_and_distinct_sources():
    items = [
        _item(source_id="src:1"),
        _item(source_id="src:2", context={}),
        _item(source_id="src:3"),
    ]
    requests = [_request(item) for item in items]

    results = plan_intake_placements(requests)

    assert [result.source_id for result in results] == ["src:1", "src:2", "src:3"]
    assert results[1].status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS


def test_batch_article_items_do_not_create_update_or_deduplicate():
    items = [
        _item(field_name="drawing", value="DRW-01", source_id="article:1", context={"article": "SYNTH01"}),
        _item(field_name="revision", value="A", source_id="article:2", context={}),
        _item(field_name="description", value="Tubo", source_id="article:3", context={"article": "SYNTH01"}),
    ]
    results = plan_intake_placements([_request(item) for item in items])

    assert [result.source_id for result in results] == ["article:1", "article:2", "article:3"]
    assert results[0].operation == PlacementOperation.NOT_AVAILABLE
    assert results[1].status == PlacementDryRunStatus.MISSING_REQUIRED_FIELDS
    assert results[1].operation == PlacementOperation.NOT_AVAILABLE
    assert results[2].operation == PlacementOperation.NOT_AVAILABLE


def test_large_batch_preserves_order_without_deduplication():
    requests = [
        _request(_item(source_id=f"batch:{index}", context={"article": "SYNTH01", "sequence": index}))
        for index in range(1000)
    ]

    results = plan_intake_placements(requests)

    assert len(results) == 1000
    assert [result.source_id for result in results[:3]] == ["batch:0", "batch:1", "batch:2"]
    assert [result.source_id for result in results[-3:]] == ["batch:997", "batch:998", "batch:999"]


def test_all_classifier_destinations_have_descriptors():
    assert set(PLACEMENT_TARGETS) == set(IntakeDestination)
    assert PLACEMENT_TARGETS[IntakeDestination.HUMAN_CONFIRMATIONS].target_repository == "article_operational_registry"
    assert all(
        descriptor.target_repository is None
        for destination, descriptor in PLACEMENT_TARGETS.items()
        if destination != IntakeDestination.HUMAN_CONFIRMATIONS
    )


def test_human_confirmation_descriptor_matches_writer_required_signature():
    signature = inspect.signature(confirm_article_operational_status)
    required = tuple(
        name
        for name, param in signature.parameters.items()
        if param.kind is inspect.Parameter.KEYWORD_ONLY
        and param.default is inspect.Parameter.empty
    )

    descriptor = PLACEMENT_TARGETS[IntakeDestination.HUMAN_CONFIRMATIONS]

    assert required == (
        "article",
        "operational_class",
        "planner_eligible",
        "tl_confirmation_required",
        "authority_role",
        "audit_note",
    )
    assert all(field in descriptor.required_fields for field in required)


def test_human_payload_separates_writer_arguments_from_source_evidence():
    result = plan_intake_placement(_request(_human_item()))

    assert set(result.payload_preview) == {"writer_arguments", "source_evidence"}
    assert "source_id" not in result.payload_preview["writer_arguments"]
    assert result.payload_preview["source_evidence"]["source_id"] == "human:SYNTH"
    assert result.payload_preview["source_evidence"]["semantic_status"] == "CERTO"


def test_no_hardcode_12514_in_dry_run_service():
    assert "12514" not in inspect.getsource(service)
