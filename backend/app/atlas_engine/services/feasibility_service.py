from __future__ import annotations

from ..domain.snapshot import Snapshot


class FeasibilityService:
    @staticmethod
    def basic_checks(snapshot: Snapshot) -> bool:
        # Deterministic minimal feasibility: station must exist
        return bool(snapshot.station and snapshot.station.name)

