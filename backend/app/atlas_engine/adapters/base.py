from __future__ import annotations

from abc import ABC, abstractmethod
from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult


class BaseAdapter(ABC):
    @abstractmethod
    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        """Return a SolveResult with keys: sequence (list[str]), meta (dict)."""
        raise NotImplementedError

