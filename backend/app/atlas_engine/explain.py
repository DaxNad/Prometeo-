from __future__ import annotations

from typing import List

from .contracts import AtlasExplanation, AtlasInput


def build_explanation(inp: AtlasInput, sequence: List[str]) -> AtlasExplanation:
    reasons: List[str] = []
    if any(e.status == "OPEN" for e in inp.events):
        reasons.append("operational event present")
    # placeholder for shared component / saturation signals
    return AtlasExplanation(reasons=reasons, risk_level="LOW", signals={})

