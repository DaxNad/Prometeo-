from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.intake_single_item_orchestrator import (
    IntakeOrchestrationStatus,
    IntakeSingleItemOrchestrationResult,
    orchestrate_intake_item,
)
from app.services.structured_intake_item_adapter import (
    StructuredIntakeAdapterResult,
    build_intake_item,
)


class StructuredIntakeFacadeStatus(str, Enum):
    ORCHESTRATED = "ORCHESTRATED"
    NOT_EXECUTED = "NOT_EXECUTED"
    ORCHESTRATION_FAILED = "ORCHESTRATION_FAILED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class StructuredIntakeFacadeResult:
    ok: bool
    status: StructuredIntakeFacadeStatus
    adapter_result: StructuredIntakeAdapterResult
    orchestration_result: IntakeSingleItemOrchestrationResult | None
    writer_called: bool
    source_id: str
    error_code: str | None = None


def process_structured_intake_payload(
    payload: Mapping[str, Any],
    *,
    requested_by_role: str | None = None,
) -> StructuredIntakeFacadeResult:
    adapter_result = build_intake_item(payload)

    if not adapter_result.ok or adapter_result.item is None:
        return StructuredIntakeFacadeResult(
            ok=False,
            status=StructuredIntakeFacadeStatus.REJECTED,
            adapter_result=adapter_result,
            orchestration_result=None,
            writer_called=False,
            source_id="",
            error_code=adapter_result.error_code,
        )

    orchestration_result = orchestrate_intake_item(
        adapter_result.item,
        requested_by_role=requested_by_role,
    )

    if orchestration_result.status == IntakeOrchestrationStatus.EXECUTED:
        status = StructuredIntakeFacadeStatus.ORCHESTRATED
    elif orchestration_result.status == IntakeOrchestrationStatus.EXECUTION_FAILED:
        status = StructuredIntakeFacadeStatus.ORCHESTRATION_FAILED
    else:
        status = StructuredIntakeFacadeStatus.NOT_EXECUTED

    return StructuredIntakeFacadeResult(
        ok=orchestration_result.ok,
        status=status,
        adapter_result=adapter_result,
        orchestration_result=orchestration_result,
        writer_called=orchestration_result.writer_called,
        source_id=orchestration_result.source_id,
        error_code=orchestration_result.error_code,
    )
