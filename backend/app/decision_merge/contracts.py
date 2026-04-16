from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AdvisorySource = Literal["atlas", "local_rule"]


@dataclass(frozen=True)
class MergeDecision:
    """Merge contract where planner decision is authoritative and advisory stays soft."""

    planner_action: str
    final_action: str
    advisory_source: AdvisorySource
    advisory_used_as_tiebreak: bool = False
