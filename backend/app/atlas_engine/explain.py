from __future__ import annotations

from typing import List

from .agent_mod import run_agent_mod_for_atlas_input
from .contracts import AtlasExplanation, AtlasInput


def build_explanation(inp: AtlasInput, sequence: List[str]) -> AtlasExplanation:
    explained = run_agent_mod_for_atlas_input(inp)
    reasons = list(explained.main_reasons or [])
    if not reasons and explained.explain_short:
        reasons = [explained.explain_short]
    if any(str(event.status).upper() == "OPEN" for event in inp.events):
        if not any("operational event present" in reason for reason in reasons):
            reasons.insert(0, "operational event present")

    risk_level = "LOW"
    if explained.decision == "BLOCK":
        risk_level = "HIGH"
    elif explained.decision == "DEFER" or explained.conflicts:
        risk_level = "MEDIUM"

    return AtlasExplanation(
        reasons=reasons,
        risk_level=risk_level,
        signals={
            "decision": explained.decision,
            "priority_score": explained.priority_score,
            "agreeing_modules": list(explained.agreeing_modules),
            "disagreeing_modules": list(explained.disagreeing_modules),
            "guard_issues": list(explained.guard_issues),
            "sequence_size": len(sequence or []),
        },
    )
