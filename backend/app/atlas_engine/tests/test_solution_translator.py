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


def test_make_plan_ortools_shared_pressure_and_open_event_signals():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
        capacities={"shared_component_pressure": True},
    )
    plan = AtlasService.make_plan(req, adapter="ortools")
    # blocked after feasible items
    assert plan.sequence[-1] == "O1"
    # shared pressure and open event reflected in meta.scoring
    scoring = plan.meta.get("scoring", {})
    assert scoring.get("penalty_shared_pressure") is True
    assert scoring.get("penalty_open_event") is True
    # explain payload contains operational event reason (post-hoc, not from solve)
    expl = plan.meta.get("explain", {})
    reasons = expl.get("reasons", [])
    assert any("operational event present" in r for r in reasons)
