from __future__ import annotations

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from .base import BaseAdapter


class ORToolsAdapter(BaseAdapter):
    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        # Placeholder: to be implemented. Raise to trigger orchestrator fallback.
        raise NotImplementedError("ORTools adapter not implemented yet")

