from __future__ import annotations

from .policy import RuntimePolicy
from .provider_factory import build_runtime_provider
from .registry import ToolRegistry
from .run_repository import AgentRunRepository
from .schemas import AgentDecision, AgentAnalyzeResponse


class AgentRuntimeService:
    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.policy = RuntimePolicy()
        self.provider = build_runtime_provider()
        self.run_repository = AgentRunRepository()

    async def analyze(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str,
        payload: dict,
    ) -> AgentAnalyzeResponse:
        inspector = self.registry.get("event_inspector")
        inspection = await inspector.run(payload)

        escalate = self.policy.should_escalate(severity=severity, inspection=inspection)

        if not escalate:
            decision = AgentDecision(
                decision_mode="local-rule",
                action="monitor",
                explanation=(
                    f"Evento {event_type} su {line_id} analizzato localmente: "
                    "nessuna escalation necessaria."
                ),
            )
            response = AgentAnalyzeResponse(
                inspection=inspection,
                decision=decision,
            )
            self.run_repository.save(
                source=source,
                line_id=line_id,
                event_type=event_type,
                severity=severity,
                inspection=inspection,
                decision_mode=decision.decision_mode,
                action=decision.action,
                explanation=decision.explanation,
            )
            return response

        provider_text = await self.provider.complete(
            f"source={source}; line_id={line_id}; event_type={event_type}; "
            f"severity={severity}; inspection={inspection}"
        )

        decision_mode = (
            "local-escalation-atlas"
            if getattr(self.provider, "name", "noop") == "atlas"
            else "local-escalation"
        )

        decision = AgentDecision(
            decision_mode=decision_mode,
            action="investigate",
            explanation=provider_text,
        )

        response = AgentAnalyzeResponse(
            inspection=inspection,
            decision=decision,
        )

        self.run_repository.save(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            inspection=inspection,
            decision_mode=decision.decision_mode,
            action=decision.action,
            explanation=decision.explanation,
        )

        return response

    async def list_runs(
        self,
        *,
        line_id: str | None = None,
        action: str | None = None,
        decision_mode: str | None = None,
        limit: int = 50,
    ):
        return self.run_repository.list_recent(
            line_id=line_id,
            action=action,
            decision_mode=decision_mode,
            limit=limit,
        )

    async def summary(
        self,
        *,
        line_id: str | None = None,
    ):
        return self.run_repository.summary(
            line_id=line_id,
        )

    async def operational_summary(
        self,
        *,
        line_id: str | None = None,
    ):
        return self.run_repository.operational_summary(
            line_id=line_id,
        )
