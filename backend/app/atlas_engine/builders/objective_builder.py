from __future__ import annotations

from ..domain.snapshot import Snapshot
from ..types import ObjectiveSpec


def build_objective(snapshot: Snapshot) -> ObjectiveSpec:
    return {
        "goals": [
            {"name": "maximize_priority"},
            {"name": "minimize_blocked"},
        ]
    }

