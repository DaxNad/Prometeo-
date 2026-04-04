from __future__ import annotations

from .decision_engine import decide
from .inspectors import inspect_event
from .run_repository import AgentRunRepository
from .schemas import AgentAnalyzeResponse


class AgentRuntimeService:
    def __init__(self) -> None:
        self.repo = AgentRunRepository()

    async def analyze(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str = "info",
        payload: dict | None = None,
    ) -> AgentAnalyzeResponse:
        payload = payload or {}

        inspection = inspect_event(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
        )

        decision = decide(inspection)

        self.repo.save(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            inspection=inspection,
            decision_mode=decision.decision_mode,
            action=decision.action,
            explanation=decision.explanation,
        )

        return AgentAnalyzeResponse(
            inspection=inspection,
            decision=decision,
        )

    async def list_runs(
        self,
        *,
        line_id: str | None = None,
        action: str | None = None,
        decision_mode: str | None = None,
        limit: int = 50,
    ) -> dict:
        items = self.repo.list_recent(
            line_id=line_id,
            action=action,
            decision_mode=decision_mode,
            limit=limit,
        )

        return {
            "ok": True,
            "count": len(items),
            "items": items,
        }

    async def summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict:
        data = self.repo.summary(line_id=line_id)

        return {
            "ok": True,
            "summary": data,
        }

    async def operational_summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict:
        data = self.repo.operational_summary(line_id=line_id)

        return {
            "ok": True,
            "summary": data,
        }

    async def status(self) -> dict:
        summary_data = self.repo.summary()

        return {
            "ok": True,
            "agent_runtime": "enabled",
            "repository": "ready",
            "summary_available": True,
            "summary_contract": {
                "has_local_rule_count": "local_rule_count" in summary_data,
                "has_local_escalation_count": "local_escalation_count" in summary_data,
                "has_escalation_total_count": "escalation_total_count" in summary_data,
                "has_atlas_escalation_count": "atlas_escalation_count" in summary_data,
            },
            "totals": {
                "total_runs": summary_data.get("total_runs", 0),
                "monitor_count": summary_data.get("monitor_count", 0),
                "investigate_count": summary_data.get("investigate_count", 0),
                "escalation_total_count": summary_data.get("escalation_total_count", 0),
                "atlas_escalation_count": summary_data.get("atlas_escalation_count", 0),
            },
        }
