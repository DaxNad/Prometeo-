from __future__ import annotations

from fastapi import APIRouter, Query

from ..agent_runtime.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse
from ..agent_runtime.service import AgentRuntimeService

router = APIRouter(prefix="/agent-runtime", tags=["agent-runtime"])


@router.post("/analyze", response_model=AgentAnalyzeResponse)
async def analyze_agent_runtime(
    payload: AgentAnalyzeRequest,
) -> AgentAnalyzeResponse:
    service = AgentRuntimeService()

    return await service.analyze(
        source=payload.source,
        line_id=payload.line_id,
        event_type=payload.event_type,
        severity=payload.severity,
        payload=payload.payload,
    )


@router.get("/runs")
async def get_runs(
    line_id: str | None = None,
    action: str | None = None,
    decision_mode: str | None = None,
    limit: int = Query(20, le=200),
):
    service = AgentRuntimeService()

    return await service.list_runs(
        line_id=line_id,
        action=action,
        decision_mode=decision_mode,
        limit=limit,
    )


@router.get("/summary")
async def get_summary(
    line_id: str | None = None,
):
    service = AgentRuntimeService()

    return await service.summary(
        line_id=line_id,
    )


@router.get("/summary/operational")
async def get_operational_summary(
    line_id: str | None = None,
):
    service = AgentRuntimeService()

    return await service.operational_summary(
        line_id=line_id,
    )
