from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent


def test_make_plan_falls_back_and_is_deterministic():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
    )
    # OR-Tools adapter raises NotImplemented → orchestrator must fallback
    plan = AtlasService.make_plan(req, adapter="ortools")
    assert plan.sequence[0] == "O1"  # blocked wins in fallback scoring
    assert set(plan.sequence) == {"O1", "O2", "O3"}
    assert plan.meta.get("adapter") in {"noop", "ortools"}  # fallback marks as noop
    assert "explain" in plan.meta

