from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.article_operational_confirmation_service import (
    ArticleOperationalConfirmationResult,
    confirm_article_operational_status,
)
from app.services.intake_destination_classifier import IntakeDestination
from app.services.intake_placement_dry_run_service import (
    IntakePlacementDryRunResult,
    PlacementDryRunStatus,
    PlacementOperation,
)


ERROR_INVALID_EXECUTION_REQUEST = "INVALID_EXECUTION_REQUEST"
ERROR_PLAN_NOT_READY = "PLAN_NOT_READY"
ERROR_UNAUTHORIZED_DESTINATION = "UNAUTHORIZED_DESTINATION"
ERROR_UNAUTHORIZED_OPERATION = "UNAUTHORIZED_OPERATION"
ERROR_UNAUTHORIZED_REPOSITORY = "UNAUTHORIZED_REPOSITORY"
ERROR_UNAUTHORIZED_SERVICE = "UNAUTHORIZED_SERVICE"
ERROR_UNAUTHORIZED_SECTION = "UNAUTHORIZED_SECTION"
ERROR_INVALID_PAYLOAD = "INVALID_PAYLOAD"
ERROR_INVALID_WRITER_ARGUMENTS = "INVALID_WRITER_ARGUMENTS"
ERROR_INVALID_SOURCE_EVIDENCE = "INVALID_SOURCE_EVIDENCE"


AUTHORIZED_DESTINATION = IntakeDestination.HUMAN_CONFIRMATIONS
AUTHORIZED_OPERATION = PlacementOperation.APPEND
AUTHORIZED_REPOSITORY = "article_operational_registry"
AUTHORIZED_SERVICE = "confirm_article_operational_status"
AUTHORIZED_SECTION = "operational_status"

WRITER_ARGUMENT_NAMES = frozenset(
    {
        "article",
        "operational_class",
        "planner_eligible",
        "tl_confirmation_required",
        "authority_role",
        "audit_note",
        "confirmed_at",
        "material",
        "drawing",
        "description",
        "confirmation_origin",
    }
)

WRITER_REQUIRED_ARGUMENT_NAMES = frozenset(
    {
        "article",
        "operational_class",
        "planner_eligible",
        "tl_confirmation_required",
        "authority_role",
        "audit_note",
    }
)


class PlacementExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    WRITER_FAILED = "WRITER_FAILED"


@dataclass(frozen=True)
class IntakePlacementExecutionResult:
    ok: bool
    status: PlacementExecutionStatus
    writer_called: bool
    source_id: str
    source_evidence: Mapping[str, Any] | None = None
    writer_result: ArticleOperationalConfirmationResult | None = None
    persisted: bool = False
    created: bool = False
    updated: bool = False
    error_code: str | None = None


def execute_intake_placement(
    plan: IntakePlacementDryRunResult,
) -> IntakePlacementExecutionResult:
    validation_error = _validate_plan(plan)
    if validation_error is not None:
        return _rejected(plan, validation_error)

    payload = plan.payload_preview
    assert isinstance(payload, Mapping)

    writer_arguments = payload["writer_arguments"]
    source_evidence = payload["source_evidence"]

    writer_result = confirm_article_operational_status(
        **dict(writer_arguments),
        source_evidence=dict(source_evidence),
    )

    return IntakePlacementExecutionResult(
        ok=writer_result.ok,
        status=(
            PlacementExecutionStatus.EXECUTED
            if writer_result.ok
            else PlacementExecutionStatus.WRITER_FAILED
        ),
        writer_called=True,
        source_id=plan.source_id,
        source_evidence=dict(source_evidence),
        writer_result=writer_result,
        persisted=writer_result.persisted,
        created=writer_result.created,
        updated=writer_result.updated,
        error_code=writer_result.error_code,
    )


def _validate_plan(plan: IntakePlacementDryRunResult) -> str | None:
    if not isinstance(plan, IntakePlacementDryRunResult):
        return ERROR_INVALID_EXECUTION_REQUEST

    if (
        plan.status != PlacementDryRunStatus.READY
        or not plan.ok
        or not plan.ready_for_persistence
        or plan.requires_review
    ):
        return ERROR_PLAN_NOT_READY

    if plan.destination != AUTHORIZED_DESTINATION:
        return ERROR_UNAUTHORIZED_DESTINATION

    if plan.operation != AUTHORIZED_OPERATION:
        return ERROR_UNAUTHORIZED_OPERATION

    if plan.target_repository != AUTHORIZED_REPOSITORY:
        return ERROR_UNAUTHORIZED_REPOSITORY

    if plan.target_service != AUTHORIZED_SERVICE:
        return ERROR_UNAUTHORIZED_SERVICE

    if plan.target_section != AUTHORIZED_SECTION:
        return ERROR_UNAUTHORIZED_SECTION

    payload = plan.payload_preview
    if not isinstance(payload, Mapping):
        return ERROR_INVALID_PAYLOAD

    if set(payload) != {"writer_arguments", "source_evidence"}:
        return ERROR_INVALID_PAYLOAD

    writer_arguments = payload.get("writer_arguments")
    if not isinstance(writer_arguments, Mapping):
        return ERROR_INVALID_WRITER_ARGUMENTS

    argument_names = set(writer_arguments)
    if not WRITER_REQUIRED_ARGUMENT_NAMES.issubset(argument_names):
        return ERROR_INVALID_WRITER_ARGUMENTS

    if not argument_names.issubset(WRITER_ARGUMENT_NAMES):
        return ERROR_INVALID_WRITER_ARGUMENTS

    source_evidence = payload.get("source_evidence")
    if not isinstance(source_evidence, Mapping):
        return ERROR_INVALID_SOURCE_EVIDENCE

    if source_evidence.get("source_id") != plan.source_id:
        return ERROR_INVALID_SOURCE_EVIDENCE

    return None


def _rejected(
    plan: Any,
    error_code: str,
) -> IntakePlacementExecutionResult:
    source_id = (
        plan.source_id
        if isinstance(plan, IntakePlacementDryRunResult)
        else ""
    )
    return IntakePlacementExecutionResult(
        ok=False,
        status=PlacementExecutionStatus.REJECTED,
        writer_called=False,
        source_id=source_id,
        error_code=error_code,
    )
