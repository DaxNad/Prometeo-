from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent


def test_make_plan_ortools_deterministic_feasible_first():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
    )
    # OR-Tools adapter deterministico: fattibile prima, bloccato in coda, priorità applicata
    plan = AtlasService.make_plan(req, adapter="ortools")
    # Feasible-first: O1 (bloccato) va in fondo, prima viene O2 (MEDIA) poi O3 (BASSA)
    assert plan.sequence[-1] == "O1"
    assert plan.sequence[0:2] == ["O2", "O3"]
    assert plan.meta.get("adapter") == "ortools"
    assert "explain" in plan.meta
