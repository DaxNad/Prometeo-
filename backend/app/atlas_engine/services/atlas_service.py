from __future__ import annotations

from ..contracts import AtlasScenarioRequest, AtlasPlan
from ..orchestrator import orchestrate
from .scenario_service import ScenarioService


class AtlasService:
    @staticmethod
    def make_plan(req: AtlasScenarioRequest, adapter: str | None = None) -> AtlasPlan:
        inp = ScenarioService.to_input(req)
        return orchestrate(inp, adapter_name=(adapter or "ortools"))

