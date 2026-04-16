from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SequencingAuthority = Literal["deterministic_planner"]


@dataclass(frozen=True)
class PlannerInput:
    """Minimal deterministic sequencing intake contract."""

    line_id: str
    station: str
    priority: str


@dataclass(frozen=True)
class PlannerOutput:
    """Deterministic sequencing result contract for downstream layers."""

    sequence_slot: int
    action: str
    authority: SequencingAuthority = "deterministic_planner"
