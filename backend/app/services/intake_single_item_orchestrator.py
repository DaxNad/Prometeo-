from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from app.services.intake_destination_classifier import (
    IntakeClassificationResult,
    IntakeItem,
    classify_intake_destination,
)
from app.services.intake_placement_dry_run_service import (
    IntakePlacementDryRunRequest,
    IntakePlacementDryRunResult,
    PlacementDryRunStatus,
    plan_intake_placement,
)
from app.services.intake_placement_execution_bridge import (
    IntakePlacementExecutionResult,
    execute_intake_placement,
)


class IntakeOrchestrationStatus(str, Enum):
    EXECUTED = "EXECUTED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    NOT_EXECUTED = "NOT_EXECUTED"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True)
class IntakeSingleItemOrchestrationResult:
    ok: bool
    status: IntakeOrchestrationStatus
    classification: IntakeClassificationResult
    plan: IntakePlacementDryRunResult | None
    execution: IntakePlacementExecutionResult | None
    writer_called: bool
    source_id: str
    error_code: str | None = None


def orchestrate_intake_item(
    item: IntakeItem,
    *,
    requested_by_role: str | None = None,
) -> IntakeSingleItemOrchestrationResult:
    classification = classify_intake_destination(item)

    if not isinstance(item, IntakeItem):
        return IntakeSingleItemOrchestrationResult(
            ok=False,
            status=IntakeOrchestrationStatus.INVALID_INPUT,
            classification=classification,
            plan=None,
            execution=None,
            writer_called=False,
            source_id=classification.source_id,
            error_code=classification.error_code,
        )

    plan = plan_intake_placement(
        IntakePlacementDryRunRequest(
            item=item,
            classification=classification,
            requested_by_role=requested_by_role,
        )
    )

    if (
        plan.status != PlacementDryRunStatus.READY
        or not plan.ok
        or not plan.ready_for_persistence
        or plan.requires_review
    ):
        return IntakeSingleItemOrchestrationResult(
            ok=False,
            status=IntakeOrchestrationStatus.NOT_EXECUTED,
            classification=classification,
            plan=plan,
            execution=None,
            writer_called=False,
            source_id=plan.source_id,
            error_code=plan.error_code or classification.error_code,
        )

    execution = execute_intake_placement(plan)

    return IntakeSingleItemOrchestrationResult(
        ok=execution.ok,
        status=(
            IntakeOrchestrationStatus.EXECUTED
            if execution.ok
            else IntakeOrchestrationStatus.EXECUTION_FAILED
        ),
        classification=classification,
        plan=plan,
        execution=execution,
        writer_called=execution.writer_called,
        source_id=execution.source_id,
        error_code=execution.error_code,
    )
