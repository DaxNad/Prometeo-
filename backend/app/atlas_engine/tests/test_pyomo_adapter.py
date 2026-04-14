from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder


def test_pyomo_adapter_deterministic_simple():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
    )
    plan = AtlasService.make_plan(req, adapter="pyomo")
    assert set(plan.sequence) == {"O1", "O2", "O3"}
    # Feasible-first: bloccato in coda
    assert plan.sequence[-1] == "O1"
    assert plan.meta.get("adapter") in {"pyomo", "noop"}


def test_pyomo_adapter_compat_shared_pressure():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="A", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="B", station="ZAW-1", priority="MEDIA", quantity=1),
        ],
        capacities={"shared_component_pressure": True, "station_queue_pressure": 1},
    )
    plan = AtlasService.make_plan(req, adapter="pyomo")
    assert plan.sequence[0] == "B"
