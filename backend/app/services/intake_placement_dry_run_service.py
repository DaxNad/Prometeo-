from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

from app.domain.authority_roles import ALLOWED_AUTHORITY_ROLES, normalize_authority_role
from app.services.intake_destination_classifier import (
    IntakeClassificationResult,
    IntakeDestination,
    IntakeItem,
)


ERROR_INVALID_PLACEMENT_REQUEST = "INVALID_PLACEMENT_REQUEST"
ERROR_DRY_RUN_REQUIRED = "DRY_RUN_REQUIRED"
ERROR_CLASSIFICATION_SOURCE_MISMATCH = "CLASSIFICATION_SOURCE_MISMATCH"
ERROR_CLASSIFICATION_VALUE_MISMATCH = "CLASSIFICATION_VALUE_MISMATCH"
ERROR_CLASSIFICATION_NOT_READY = "CLASSIFICATION_NOT_READY"
ERROR_DESTINATION_MISSING = "DESTINATION_MISSING"
ERROR_UNSUPPORTED_DESTINATION = "UNSUPPORTED_DESTINATION"
ERROR_TARGET_NOT_AVAILABLE = "TARGET_NOT_AVAILABLE"
ERROR_MISSING_REQUIRED_FIELDS = "MISSING_REQUIRED_FIELDS"
ERROR_SOURCE_NOT_AUTHORIZED = "SOURCE_NOT_AUTHORIZED"
ERROR_AUTHORITY_REQUIRED = "AUTHORITY_REQUIRED"
ERROR_INVALID_PAYLOAD_PREVIEW = "INVALID_PAYLOAD_PREVIEW"
ERROR_INVALID_TARGET_PAYLOAD = "INVALID_TARGET_PAYLOAD"


class PlacementDryRunStatus(str, Enum):
    READY = "READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNSUPPORTED_DESTINATION = "UNSUPPORTED_DESTINATION"
    TARGET_NOT_AVAILABLE = "TARGET_NOT_AVAILABLE"
    INVALID_PLACEMENT_REQUEST = "INVALID_PLACEMENT_REQUEST"
    SOURCE_NOT_AUTHORIZED = "SOURCE_NOT_AUTHORIZED"
    AUTHORITY_REQUIRED = "AUTHORITY_REQUIRED"
    MISSING_REQUIRED_FIELDS = "MISSING_REQUIRED_FIELDS"


class PlacementOperation(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    APPEND = "APPEND"
    LINK = "LINK"
    NO_OP = "NO_OP"
    NOT_AVAILABLE = "NOT_AVAILABLE"


@dataclass(frozen=True)
class IntakePlacementDryRunRequest:
    item: IntakeItem
    classification: IntakeClassificationResult
    requested_by_role: str | None = None
    dry_run: bool = True


@dataclass(frozen=True)
class PlacementTargetDescriptor:
    destination: IntakeDestination
    domain_entity: str
    target_repository: str | None
    target_service: str | None
    target_section: str
    required_fields: tuple[str, ...]
    source_policy: str
    authority_policy: str
    audit_policy: str


@dataclass(frozen=True)
class IntakePlacementDryRunResult:
    ok: bool
    status: PlacementDryRunStatus
    destination: IntakeDestination | None
    domain_entity: str | None
    target_repository: str | None
    target_service: str | None
    target_section: str | None
    operation: PlacementOperation
    payload_preview: Mapping[str, Any] | None
    required_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    matched_rules: tuple[str, ...]
    source_id: str
    source_status: str | None
    semantic_status: str | None
    authority_role: str | None
    ready_for_persistence: bool
    requires_review: bool
    review_reason: str | None
    error_code: str | None = None


PLACEMENT_TARGETS: Mapping[IntakeDestination, PlacementTargetDescriptor] = MappingProxyType(
    {
        IntakeDestination.ARTICLE: PlacementTargetDescriptor(
            destination=IntakeDestination.ARTICLE,
            domain_entity="Article",
            target_repository=None,
            target_service=None,
            target_section="article_metadata",
            required_fields=("article", "field_name", "value", "source_id"),
            source_policy="preview and unverified sources require review; no semantic promotion",
            authority_policy="authority required only for operational status changes",
            audit_policy="source evidence must be preserved separately",
        ),
        IntakeDestination.ROUTE: PlacementTargetDescriptor(
            destination=IntakeDestination.ROUTE,
            domain_entity="Route",
            target_repository=None,
            target_service=None,
            target_section="route_step",
            required_fields=("article", "operation_name", "sequence", "source_id"),
            source_policy="route preview is not authoritative by itself",
            authority_policy="authorized operational validation required before persistence",
            audit_policy="operation source evidence must remain distinct",
        ),
        IntakeDestination.COMPONENTS: PlacementTargetDescriptor(
            destination=IntakeDestination.COMPONENTS,
            domain_entity="ArticleComponentRelation",
            target_repository=None,
            target_service=None,
            target_section="bom_component",
            required_fields=("article", "component_code", "quantity", "source_id"),
            source_policy="BOM evidence must preserve source identity",
            authority_policy="authorized validation required before authoritative BOM update",
            audit_policy="component relation evidence must remain distinct",
        ),
        IntakeDestination.TOOLS: PlacementTargetDescriptor(
            destination=IntakeDestination.TOOLS,
            domain_entity="ToolRequirement",
            target_repository=None,
            target_service=None,
            target_section="tooling_requirement",
            required_fields=("article", "tool_name", "source_id"),
            source_policy="tooling preview is not station creation",
            authority_policy="authorized validation required before tooling persistence",
            audit_policy="tool evidence must remain distinct",
        ),
        IntakeDestination.QUALITY_CONTROLS: PlacementTargetDescriptor(
            destination=IntakeDestination.QUALITY_CONTROLS,
            domain_entity="QualityControlRequirement",
            target_repository=None,
            target_service=None,
            target_section="quality_control",
            required_fields=("article", "control_name", "source_id"),
            source_policy="quality preview is not route persistence",
            authority_policy="authorized validation required before authoritative quality update",
            audit_policy="original and normalized values must be preserved",
        ),
        IntakeDestination.CONSTRAINTS: PlacementTargetDescriptor(
            destination=IntakeDestination.CONSTRAINTS,
            domain_entity="OperationalConstraint",
            target_repository=None,
            target_service=None,
            target_section="constraint",
            required_fields=("subject", "constraint_text", "source_id"),
            source_policy="constraint source must be reviewable",
            authority_policy="authorized validation required for blocking rules",
            audit_policy="constraint text must be preserved without interpretation",
        ),
        IntakeDestination.HUMAN_CONFIRMATIONS: PlacementTargetDescriptor(
            destination=IntakeDestination.HUMAN_CONFIRMATIONS,
            domain_entity="HumanOperationalConfirmation",
            target_repository="article_operational_registry",
            target_service="confirm_article_operational_status",
            target_section="operational_status",
            required_fields=(
                "article",
                "operational_class",
                "planner_eligible",
                "tl_confirmation_required",
                "authority_role",
                "audit_note",
                "confirmation_origin",
            ),
            source_policy="human explicit confirmation requires governed authority",
            authority_policy="RESPONSABILE_PRODUZIONE required",
            audit_policy="confirmation must be persisted only by governed confirmation service",
        ),
    }
)

_UNSET = object()


def plan_intake_placement(
    request: IntakePlacementDryRunRequest,
) -> IntakePlacementDryRunResult:
    invalid = _validate_request_shape(request)
    if invalid is not None:
        return invalid

    item = request.item
    classification = request.classification
    if classification.requires_review:
        return _base_result(
            item=item,
            classification=classification,
            status=PlacementDryRunStatus.REVIEW_REQUIRED,
            destination=classification.destination,
            operation=PlacementOperation.NOT_AVAILABLE,
            blocking_reasons=(classification.review_reason or ERROR_CLASSIFICATION_NOT_READY,),
            requires_review=True,
            review_reason=classification.review_reason or "Classification requires review.",
            error_code=ERROR_CLASSIFICATION_NOT_READY,
        )

    if classification.destination is None:
        return _invalid_shape_result(ERROR_DESTINATION_MISSING, item=item, classification=classification)

    descriptor = PLACEMENT_TARGETS.get(classification.destination)
    if descriptor is None:
        return _base_result(
            item=item,
            classification=classification,
            status=PlacementDryRunStatus.UNSUPPORTED_DESTINATION,
            destination=classification.destination,
            operation=PlacementOperation.NOT_AVAILABLE,
            blocking_reasons=(ERROR_UNSUPPORTED_DESTINATION,),
            requires_review=True,
            review_reason="Destination has no governed placement descriptor.",
            error_code=ERROR_UNSUPPORTED_DESTINATION,
        )

    source_block = _source_block_result(item=item, classification=classification, descriptor=descriptor)
    if source_block is not None:
        return source_block

    plan = _plan_by_destination(item, classification, descriptor)
    if plan.status != PlacementDryRunStatus.READY:
        return plan

    policy_result = _apply_source_policy(item=item, classification=classification, descriptor=descriptor, plan=plan)
    if policy_result is not None:
        return policy_result

    if plan.target_service is None:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.TARGET_NOT_AVAILABLE,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=plan.payload_preview,
            required_fields=plan.required_fields,
            target_repository=plan.target_repository,
            target_service=plan.target_service,
            target_section=plan.target_section,
            warnings=plan.warnings,
            blocking_reasons=("No governed writer service is available for this destination.",),
            requires_review=True,
            review_reason="Logical target exists, but no governed persistence service is available.",
            error_code=ERROR_TARGET_NOT_AVAILABLE,
        )

    return plan


def plan_intake_placements(
    requests: Sequence[IntakePlacementDryRunRequest],
) -> list[IntakePlacementDryRunResult]:
    return [plan_intake_placement(request) for request in requests]


def _plan_by_destination(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    destination = classification.destination
    if destination == IntakeDestination.ARTICLE:
        return _plan_article_placement(item, classification, descriptor)
    if destination == IntakeDestination.ROUTE:
        return _plan_route_placement(item, classification, descriptor)
    if destination == IntakeDestination.COMPONENTS:
        return _plan_component_placement(item, classification, descriptor)
    if destination == IntakeDestination.TOOLS:
        return _plan_tool_placement(item, classification, descriptor)
    if destination == IntakeDestination.QUALITY_CONTROLS:
        return _plan_quality_control_placement(item, classification, descriptor)
    if destination == IntakeDestination.CONSTRAINTS:
        return _plan_constraint_placement(item, classification, descriptor)
    if destination == IntakeDestination.HUMAN_CONFIRMATIONS:
        return _plan_human_confirmation_placement(item, classification, descriptor)

    return _descriptor_result(
        item=item,
        classification=classification,
        descriptor=descriptor,
        status=PlacementDryRunStatus.UNSUPPORTED_DESTINATION,
        operation=PlacementOperation.NOT_AVAILABLE,
        blocking_reasons=(ERROR_UNSUPPORTED_DESTINATION,),
        requires_review=True,
        review_reason="Destination is not supported by dry-run placement.",
        error_code=ERROR_UNSUPPORTED_DESTINATION,
    )


def _plan_article_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    field_name = classification.normalized_field_name or _clean(item.field_name)
    article = _article_from_item(item, classification)
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "article": article,
            "field_name": field_name,
            "value": classification.normalized_value,
            "source_value": classification.original_value,
        },
    )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.NOT_AVAILABLE,
        payload_preview=payload,
        values={"article": article, "field_name": field_name, "value": classification.normalized_value},
    )


def _plan_route_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    article = _article_from_item(item, classification)
    sequence = _lookup(item, "sequence") or _lookup(item, "operation_index")
    station = _lookup(item, "station")
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "article": article,
            "operation_name": classification.normalized_value,
            "sequence": sequence,
            "station": station,
        },
    )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.APPEND,
        payload_preview=payload,
        values={
            "article": article,
            "operation_name": classification.normalized_value,
            "sequence": sequence,
        },
    )


def _plan_component_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    article = _article_from_item(item, classification)
    component_code = _lookup(item, "component_code") or _lookup(item, "code") or classification.normalized_value
    quantity = _lookup(item, "quantity") or _lookup(item, "qty") or _lookup(item, "qta")
    relation_type = _lookup(item, "relation_type") or _lookup(item, "type")
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "article": article,
            "component_code": component_code,
            "quantity": quantity,
            "relation_type": relation_type,
        },
    )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.LINK,
        payload_preview=payload,
        values={"article": article, "component_code": component_code, "quantity": quantity},
    )


def _plan_tool_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    article = _article_from_item(item, classification)
    station = _lookup(item, "station")
    requirement_type = _lookup(item, "requirement_type") or _lookup(item, "type")
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "article": article,
            "tool_name": classification.normalized_value,
            "station": station,
            "requirement_type": requirement_type,
        },
    )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.LINK,
        payload_preview=payload,
        values={"article": article, "tool_name": classification.normalized_value},
    )


def _plan_quality_control_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    article = _article_from_item(item, classification)
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "article": article,
            "control_name": classification.normalized_value,
            "source_value": classification.original_value,
            "normalization_rules_applied": classification.normalization_rules_applied,
            "route_relation": _lookup(item, "route_step") or _lookup(item, "operation_index"),
        },
    )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.LINK,
        payload_preview=payload,
        values={"article": article, "control_name": classification.normalized_value},
        warnings=("Quality controls are not duplicated into Route by dry-run placement.",),
    )


def _plan_constraint_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    subject = _lookup(item, "subject") or _article_from_item(item, classification)
    payload = _source_payload(
        item=item,
        classification=classification,
        extra={
            "subject": subject,
            "constraint_text": classification.normalized_value,
            "blocking_flag": _lookup(item, "blocking_flag"),
        },
    )
    if not subject:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.REVIEW_REQUIRED,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=payload,
            missing_fields=("subject",),
            blocking_reasons=("Constraint subject is not determinable from item context.",),
            requires_review=True,
            review_reason="Constraint subject must be reviewed before placement.",
            error_code=ERROR_MISSING_REQUIRED_FIELDS,
        )
    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.APPEND,
        payload_preview=payload,
        values={"subject": subject, "constraint_text": classification.normalized_value},
    )


def _plan_human_confirmation_placement(
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult:
    authority_role = normalize_authority_role(item.authority_role)
    if not authority_role or authority_role not in ALLOWED_AUTHORITY_ROLES:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.AUTHORITY_REQUIRED,
            operation=PlacementOperation.NOT_AVAILABLE,
            blocking_reasons=("Allowed authority_role is required for human confirmation placement.",),
            requires_review=True,
            review_reason="Human confirmation requires a governed authority role.",
            error_code=ERROR_AUTHORITY_REQUIRED,
        )

    article = _article_from_item(item, classification)
    confirmed_field = _lookup(item, "confirmed_field") or classification.normalized_field_name
    confirmation_origin = _lookup(item, "confirmation_origin")
    audit_note = _lookup(item, "audit_note") or _lookup(item, "evidence")
    target_service = (
        descriptor.target_service
        if str(confirmed_field or "").strip().lower()
        in {"operational_class", "status", "stato_operativo", "operational_status"}
        else None
    )
    if target_service is None:
        payload = _human_confirmation_payload(
            item=item,
            classification=classification,
            writer_arguments={
                "article": article,
                "confirmed_field": confirmed_field,
                "confirmed_value": _lookup(item, "confirmed_value") or classification.normalized_value,
                "authority_role": authority_role,
                "confirmation_origin": confirmation_origin,
                "audit_note": audit_note,
            },
        )
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=PlacementTargetDescriptor(
                destination=descriptor.destination,
                domain_entity=descriptor.domain_entity,
                target_repository=descriptor.target_repository,
                target_service=None,
                target_section=descriptor.target_section,
                required_fields=descriptor.required_fields,
                source_policy=descriptor.source_policy,
                authority_policy=descriptor.authority_policy,
                audit_policy=descriptor.audit_policy,
            ),
            status=PlacementDryRunStatus.TARGET_NOT_AVAILABLE,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=payload,
            blocking_reasons=("No governed writer service is available for this human confirmation field.",),
            requires_review=True,
            review_reason="Only operational status confirmations map to confirm_article_operational_status.",
            error_code=ERROR_TARGET_NOT_AVAILABLE,
        )

    operational_class = _operational_class_from_confirmation(item, classification)
    writer_arguments = {
        "article": article,
        "operational_class": operational_class,
        "planner_eligible": _lookup(item, "planner_eligible"),
        "tl_confirmation_required": _lookup(item, "tl_confirmation_required"),
        "authority_role": authority_role,
        "audit_note": audit_note,
        "confirmation_origin": confirmation_origin,
        "confirmed_at": _lookup(item, "confirmed_at"),
        "material": _lookup(item, "material"),
        "drawing": _lookup(item, "drawing"),
        "description": _lookup(item, "description"),
    }
    payload = _human_confirmation_payload(
        item=item,
        classification=classification,
        writer_arguments=writer_arguments,
    )
    invalid_fields = tuple(
        field
        for field in ("planner_eligible", "tl_confirmation_required")
        if writer_arguments[field] is not None and not isinstance(writer_arguments[field], bool)
    )
    if invalid_fields:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.INVALID_PLACEMENT_REQUEST,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=payload,
            blocking_reasons=tuple(f"Invalid boolean field: {field}" for field in invalid_fields),
            requires_review=True,
            review_reason="Writer boolean arguments must be real bool values.",
            error_code=ERROR_INVALID_TARGET_PAYLOAD,
        )

    return _complete_or_missing(
        item=item,
        classification=classification,
        descriptor=descriptor,
        operation=PlacementOperation.APPEND,
        payload_preview=payload,
        values=writer_arguments,
    )


def _human_confirmation_payload(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    writer_arguments: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "writer_arguments": dict(writer_arguments),
        "source_evidence": {
            "source_id": item.source_id,
            "source_status": item.source_status,
            "semantic_status": item.semantic_status,
            "matched_rules": classification.matched_rules,
        },
    }


def _operational_class_from_confirmation(
    item: IntakeItem,
    classification: IntakeClassificationResult,
) -> Any:
    confirmed_field = str(_lookup(item, "confirmed_field") or classification.normalized_field_name).strip().lower()
    if confirmed_field == "operational_class":
        confirmed_value = _lookup(item, "confirmed_value")
        if not _is_empty(confirmed_value):
            return confirmed_value
    if classification.normalized_field_name == "operational_class":
        return classification.normalized_value
    return _lookup(item, "operational_class")


def _complete_or_missing(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
    operation: PlacementOperation,
    payload_preview: Mapping[str, Any],
    values: Mapping[str, Any],
    warnings: tuple[str, ...] = (),
) -> IntakePlacementDryRunResult:
    missing = tuple(field for field in descriptor.required_fields if _is_empty(values.get(field)) and field != "source_id")
    if missing:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.MISSING_REQUIRED_FIELDS,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=payload_preview,
            missing_fields=missing,
            warnings=warnings,
            blocking_reasons=tuple(f"Missing required field: {field}" for field in missing),
            requires_review=True,
            review_reason="Required fields are missing for target placement.",
            error_code=ERROR_MISSING_REQUIRED_FIELDS,
        )

    return _descriptor_result(
        item=item,
        classification=classification,
        descriptor=descriptor,
        status=PlacementDryRunStatus.READY,
        operation=operation,
        payload_preview=payload_preview,
        warnings=warnings,
        ready_for_persistence=descriptor.target_service is not None,
        requires_review=False,
        review_reason=None,
    )


def _validate_request_shape(request: IntakePlacementDryRunRequest) -> IntakePlacementDryRunResult | None:
    if not isinstance(request, IntakePlacementDryRunRequest):
        return _invalid_shape_result(ERROR_INVALID_PLACEMENT_REQUEST)

    item = request.item
    classification = request.classification
    source_id = _clean(getattr(item, "source_id", ""))

    if request.dry_run is not True:
        return _invalid_shape_result(ERROR_DRY_RUN_REQUIRED, item=item, classification=classification)

    if not source_id:
        return _invalid_shape_result(ERROR_INVALID_PLACEMENT_REQUEST, item=item, classification=classification)

    if request.requested_by_role and normalize_authority_role(request.requested_by_role) not in ALLOWED_AUTHORITY_ROLES:
        return _invalid_shape_result(ERROR_AUTHORITY_REQUIRED, item=item, classification=classification)

    if classification.source_id != item.source_id:
        return _invalid_shape_result(ERROR_CLASSIFICATION_SOURCE_MISMATCH, item=item, classification=classification)

    if _comparable_value(item.value) and classification.original_value != item.value:
        return _invalid_shape_result(ERROR_CLASSIFICATION_VALUE_MISMATCH, item=item, classification=classification)

    if classification.ok is not True:
        return _invalid_shape_result(ERROR_CLASSIFICATION_NOT_READY, item=item, classification=classification)

    return None


def _source_block_result(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
) -> IntakePlacementDryRunResult | None:
    source_status = _clean(item.source_status or classification.source_id).upper()
    if source_status == "SOURCE_FORBIDDEN":
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.SOURCE_NOT_AUTHORIZED,
            operation=PlacementOperation.NOT_AVAILABLE,
            blocking_reasons=("Source status is SOURCE_FORBIDDEN.",),
            requires_review=True,
            review_reason="Source is not authorized for placement.",
            error_code=ERROR_SOURCE_NOT_AUTHORIZED,
        )
    if source_status in {"SOURCE_MISSING", "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"}:
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.BLOCKED,
            operation=PlacementOperation.NOT_AVAILABLE,
            blocking_reasons=(f"Source status is {source_status}.",),
            requires_review=True,
            review_reason="Source is unavailable for placement.",
            error_code=source_status,
        )
    return None


def _apply_source_policy(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
    plan: IntakePlacementDryRunResult,
) -> IntakePlacementDryRunResult | None:
    source_status = _clean(item.source_status).upper()
    semantic_status = _clean(item.semantic_status or classification.confidence).upper()
    if source_status == "PREVIEW_ONLY" or semantic_status == "DA_VERIFICARE":
        return _descriptor_result(
            item=item,
            classification=classification,
            descriptor=descriptor,
            status=PlacementDryRunStatus.REVIEW_REQUIRED,
            operation=PlacementOperation.NOT_AVAILABLE,
            payload_preview=plan.payload_preview,
            required_fields=plan.required_fields,
            warnings=plan.warnings + ("READY does not mean CERTO; source policy requires review.",),
            blocking_reasons=("Preview or DA_VERIFICARE source cannot be persisted as authoritative data.",),
            requires_review=True,
            review_reason="Source policy requires review before governed persistence.",
            error_code=ERROR_CLASSIFICATION_NOT_READY,
        )
    return None


def _descriptor_result(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    descriptor: PlacementTargetDescriptor,
    status: PlacementDryRunStatus,
    operation: PlacementOperation,
    payload_preview: Mapping[str, Any] | None = None,
    target_repository: str | None | object = _UNSET,
    target_service: str | None | object = _UNSET,
    target_section: str | None | object = _UNSET,
    required_fields: tuple[str, ...] | None = None,
    missing_fields: tuple[str, ...] = (),
    blocking_reasons: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
    ready_for_persistence: bool = False,
    requires_review: bool = True,
    review_reason: str | None = None,
    error_code: str | None = None,
) -> IntakePlacementDryRunResult:
    return IntakePlacementDryRunResult(
        ok=status == PlacementDryRunStatus.READY,
        status=status,
        destination=classification.destination,
        domain_entity=descriptor.domain_entity,
        target_repository=descriptor.target_repository if target_repository is _UNSET else target_repository,
        target_service=descriptor.target_service if target_service is _UNSET else target_service,
        target_section=descriptor.target_section if target_section is _UNSET else target_section,
        operation=operation,
        payload_preview=dict(payload_preview) if payload_preview is not None else None,
        required_fields=required_fields or descriptor.required_fields,
        missing_fields=missing_fields,
        blocking_reasons=blocking_reasons,
        warnings=warnings,
        matched_rules=classification.matched_rules,
        source_id=item.source_id,
        source_status=item.source_status,
        semantic_status=item.semantic_status,
        authority_role=normalize_authority_role(item.authority_role) or None,
        ready_for_persistence=ready_for_persistence and status == PlacementDryRunStatus.READY,
        requires_review=requires_review,
        review_reason=review_reason,
        error_code=error_code,
    )


def _base_result(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    status: PlacementDryRunStatus,
    destination: IntakeDestination | None,
    operation: PlacementOperation,
    blocking_reasons: tuple[str, ...],
    requires_review: bool,
    review_reason: str,
    error_code: str,
) -> IntakePlacementDryRunResult:
    return IntakePlacementDryRunResult(
        ok=False,
        status=status,
        destination=destination,
        domain_entity=None,
        target_repository=None,
        target_service=None,
        target_section=None,
        operation=operation,
        payload_preview=None,
        required_fields=(),
        missing_fields=(),
        blocking_reasons=blocking_reasons,
        warnings=(),
        matched_rules=classification.matched_rules,
        source_id=item.source_id,
        source_status=item.source_status,
        semantic_status=item.semantic_status,
        authority_role=normalize_authority_role(item.authority_role) or None,
        ready_for_persistence=False,
        requires_review=requires_review,
        review_reason=review_reason,
        error_code=error_code,
    )


def _invalid_shape_result(
    error_code: str,
    *,
    item: IntakeItem | None = None,
    classification: IntakeClassificationResult | None = None,
) -> IntakePlacementDryRunResult:
    return IntakePlacementDryRunResult(
        ok=False,
        status=PlacementDryRunStatus.INVALID_PLACEMENT_REQUEST,
        destination=getattr(classification, "destination", None),
        domain_entity=None,
        target_repository=None,
        target_service=None,
        target_section=None,
        operation=PlacementOperation.NOT_AVAILABLE,
        payload_preview=None,
        required_fields=(),
        missing_fields=(),
        blocking_reasons=(error_code,),
        warnings=(),
        matched_rules=getattr(classification, "matched_rules", ()),
        source_id=getattr(item, "source_id", ""),
        source_status=getattr(item, "source_status", None),
        semantic_status=getattr(item, "semantic_status", None),
        authority_role=normalize_authority_role(getattr(item, "authority_role", None)) or None,
        ready_for_persistence=False,
        requires_review=True,
        review_reason=error_code,
        error_code=error_code,
    )


def _source_payload(
    *,
    item: IntakeItem,
    classification: IntakeClassificationResult,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    payload = dict(extra)
    payload.update(
        {
            "source_id": item.source_id,
            "source_status": item.source_status,
            "semantic_status": item.semantic_status,
            "original_value": classification.original_value,
            "normalized_value": classification.normalized_value,
        }
    )
    return payload


def _article_from_item(item: IntakeItem, classification: IntakeClassificationResult) -> Any:
    for key in ("article", "articolo", "subject"):
        value = _lookup(item, key)
        if not _is_empty(value):
            return value
    if classification.destination == IntakeDestination.ARTICLE and classification.normalized_field_name in {
        "article",
        "articolo",
        "article_code",
    }:
        return classification.normalized_value
    return None


def _lookup(item: IntakeItem, key: str) -> Any:
    for container in (item.context, item.metadata, item.value if isinstance(item.value, Mapping) else None):
        if isinstance(container, Mapping) and key in container:
            return container[key]
    return None


def _comparable_value(value: Any) -> bool:
    return not isinstance(value, (list, tuple, set, frozenset))


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _clean(value: Any) -> str:
    return str(value or "").strip()
