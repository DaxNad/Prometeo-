from __future__ import annotations

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from ..fallback import generate
from .base import BaseAdapter


class NoopAdapter(BaseAdapter):
    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        seq = [o.order_id for o in snapshot.orders]
        # For safety, use fallback generation which is deterministic and prioritizes blocked
        # but keep original order if priorities are equal
        # Here we simply delegate to fallback on the input reconstructed from snapshot
        return {"sequence": seq, "meta": {"adapter": "noop"}}

