from app.atlas_engine.agent_mod import build_raw_signals_from_atlas_input, run_agent_mod_for_atlas_input
from app.atlas_engine.contracts import AtlasEvent, AtlasInput, AtlasOrder
from app.atlas_engine.explain import build_explanation


def test_build_raw_signals_from_atlas_input_maps_minimal_operational_context():
    inp = AtlasInput(
        station="ZAW-1",
        orders=[AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA")],
        events=[AtlasEvent(station="ZAW-1", title="QUEUE", status="OPEN")],
        capacities={"station_queue_pressure": 0.8, "shared_component_pressure": True},
    )

    raw_signals = build_raw_signals_from_atlas_input(inp)

    assert raw_signals["shipment_priority_result"]["decision"] == "boost"
    assert raw_signals["line_capacity_result"]["decision"] == "warning"
    assert raw_signals["bottleneck_pressure_result"]["decision"] == "defer"
    assert raw_signals["component_availability_result"]["decision"] == "defer"


def test_build_explanation_uses_agent_mod_pipeline_without_touching_solver():
    inp = AtlasInput(
        station="ZAW-1",
        orders=[AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA")],
        events=[AtlasEvent(station="ZAW-1", title="QUEUE", status="OPEN")],
        capacities={"station_queue_pressure": 0.8},
    )

    explained = run_agent_mod_for_atlas_input(inp)
    expl = build_explanation(inp, ["O1"])

    assert explained.decision == "DEFER"
    assert any("open operational event" in reason for reason in expl.reasons)
    assert expl.risk_level == "MEDIUM"
    assert expl.signals["decision"] == "DEFER"
    assert "bottleneck_pressure" in expl.signals["agreeing_modules"]
