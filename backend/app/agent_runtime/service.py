from __future__ import annotations

from .decision_engine import decide
from .inspectors import inspect_event
from .run_repository import AgentRunRepository
from .schemas import AgentAnalyzeResponse
from .architecture_guard import evaluate_architecture, summarize_guard_result
from app.services.anthropic_provider import claude_chat
from app.services.prompt_builder import build_agent_runtime_prompt


class AgentRuntimeService:
    def __init__(self) -> None:
        self.repo = AgentRunRepository()

    def _build_architecture_context(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str,
        payload: dict,
    ) -> dict:
        payload = payload or {}

        return {
            "breaks_order_event_model": bool(payload.get("breaks_order_event_model", False)),
            "introduces_hardcode": bool(payload.get("introduces_hardcode", False)),
            "duplicates_domain_logic": bool(payload.get("duplicates_domain_logic", False)),
            "crud_drift": bool(payload.get("crud_drift", False)),
            "reduces_explainability": bool(payload.get("reduces_explainability", False)),
            "changes_semantic_registry": bool(payload.get("changes_semantic_registry", False)),
            "changes_planner_logic": bool(
                payload.get("changes_planner_logic", False)
                or event_type in {"turn_plan_requested", "sequence_requested", "machine_load_requested"}
                or source in {"planner", "atlas_engine"}
            ),
        }

    def _build_explanation_with_claude(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str,
        payload: dict,
        inspection: dict,
        local_action: str,
        fallback_explanation: str | None,
    ) -> str:
        try:
            prompt = build_agent_runtime_prompt(
                source=source,
                line_id=line_id,
                event_type=event_type,
                severity=severity,
                payload=payload,
                inspection=inspection,
                local_decision_action=local_action,
            )

            result = claude_chat(
                prompt=prompt,
                max_tokens=180,
                temperature=0.1,
            )

            text = result.get("text", "").strip()
            if text:
                return text

        except Exception:
            pass

        return fallback_explanation or (
            f"AZIONE_TL: {local_action}\n"
            f"MOTIVO: spiegazione non disponibile\n"
            f"PRIORITA: {severity.upper()}"
        )

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

        architecture_context = self._build_architecture_context(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
        )
        architecture_result = evaluate_architecture(architecture_context)
        architecture_summary = summarize_guard_result(architecture_result)

        inspection = inspect_event(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
        )

        inspection["architecture_guard"] = architecture_summary

        decision = decide(inspection)

        if architecture_summary.get("status") == "REVIEW":
            decision.decision_mode = "architecture_guard"
            decision.action = "INVESTIGATE"

            existing_explanation = decision.explanation or ""
            guard_notes = architecture_summary.get("notes") or []
            joined_notes = "; ".join(guard_notes) if guard_notes else "architectural review required"

            decision.explanation = (
                f"{existing_explanation}\nARCHITECTURE_GUARD: {joined_notes}".strip()
            )

        decision.explanation = self._build_explanation_with_claude(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
            inspection=inspection,
            local_action=decision.action,
            fallback_explanation=decision.explanation,
        )

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
