from __future__ import annotations

from typing import Any

from .schemas import AgentDecision


def decide(
    inspection: dict[str, Any],
) -> AgentDecision:

    if inspection.get("possible_anomaly"):

        return AgentDecision(
            decision_mode="local-escalation",
            action="investigate",
            explanation="possible anomaly detected"
        )

    return AgentDecision(
        decision_mode="local-rule",
        action="monitor",
        explanation="normal condition"
    )
