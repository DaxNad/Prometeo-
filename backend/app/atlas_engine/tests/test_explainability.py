from backend.app.atlas_engine.explain import build_explanation
from backend.app.atlas_engine.contracts import AtlasInput, AtlasOrder, AtlasEvent


def test_explain_open_event_signal():
    inp = AtlasInput(
        station="ZAW-1",
        orders=[AtlasOrder(order_id="O1", station="ZAW-1")],
        events=[AtlasEvent(station="ZAW-1", title="queue", status="OPEN")],
    )
    expl = build_explanation(inp, ["O1"])
    assert any("operational event present" in r for r in expl.reasons)

