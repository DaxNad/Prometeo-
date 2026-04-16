from backend.app.atlas_engine.builders.snapshot_builder import build_snapshot
from backend.app.atlas_engine.builders.constraint_builder import build_constraints
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder


def test_build_constraints_structure_deterministic():
    req = AtlasScenarioRequest(station="ZAW-1", orders=[AtlasOrder(order_id="O1", station="ZAW-1")])
    snap = build_snapshot(req)
    cons = build_constraints(snap)
    assert cons["hard"][0]["name"] == "station_consistency"
    assert cons["hard"][0]["station"] == "ZAW-1"
    assert cons["soft"][0]["name"] == "priority_respect"

