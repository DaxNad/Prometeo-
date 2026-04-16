from __future__ import annotations

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet


def build_constraints(snapshot: Snapshot) -> ConstraintSet:
    # placeholder deterministic structure
    return {
        "hard": [
            {"name": "station_consistency", "station": snapshot.station.name},
        ],
        "soft": [
            {"name": "priority_respect"},
        ],
    }

