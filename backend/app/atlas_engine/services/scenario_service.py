from __future__ import annotations

from ..contracts import AtlasScenarioRequest, AtlasInput


class ScenarioService:
    @staticmethod
    def to_input(req: AtlasScenarioRequest) -> AtlasInput:
        return AtlasInput(
            station=req.station,
            orders=list(req.orders),
            events=list(req.events),
            capacities=dict(req.capacities or {}),
        )

