from backend.app.atlas_engine.builders.snapshot_builder import build_snapshot
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent


def test_build_snapshot_zaw1_minimal():
    req = AtlasScenarioRequest(
        station="ZAW_1",
        orders=[
            AtlasOrder(order_id="O1", station="ZAW-1", quantity=5, priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O2", station="ZAW-1", quantity=3, priority="MEDIA"),
            AtlasOrder(order_id="O3", station="ZAW-1", quantity=2, priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="queue pressure", status="OPEN", event_type="QUEUE")],
    )
    snap = build_snapshot(req)
    assert snap.station.name == "ZAW-1"
    assert len(snap.orders) == 3
    assert any(e.status == "OPEN" for e in snap.events)

