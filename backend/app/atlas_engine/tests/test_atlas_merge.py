from app.atlas_engine.merge.atlas_merge import (
    AnalyzerSignal,
    merge_order_signals,
    merge_all,
)


def test_blocking_constraint_wins_over_positive_scores():
    signals = [
        AnalyzerSignal(module_name="events", order_id="A1", status="BLOCK", blocking_constraints=["OPEN_EVENT@ZAW-1"], reasons=["evento operativo aperto"]),
        AnalyzerSignal(module_name="priority", order_id="A1", status="BOOST", priority_delta=+0.5, reasons=["cliente ALTA"]),
        AnalyzerSignal(module_name="station", order_id="A1", status="OK", priority_delta=+0.1),
    ]
    res = merge_order_signals("A1", signals)
    assert res["merge_result"] == "BLOCK"
    assert "OPEN_EVENT@ZAW-1" in res["active_constraints"]


def test_positive_convergence_returns_boost_or_allow():
    signals = [
        AnalyzerSignal(module_name="priority", order_id="B1", status="BOOST", priority_delta=+0.4, reasons=["cliente ALTA"]),
        AnalyzerSignal(module_name="station", order_id="B1", status="OK", priority_delta=+0.2),
    ]
    res = merge_order_signals("B1", signals)
    assert res["merge_result"] in {"BOOST", "ALLOW"}
    assert res["final_priority"] >= 0.5


def test_strong_conflict_yields_defer_or_investigate():
    signals = [
        AnalyzerSignal(module_name="priority", order_id="C1", status="BOOST", priority_delta=+0.4, reasons=["cliente ALTA"]),
        AnalyzerSignal(module_name="station", order_id="C1", status="WARNING", priority_delta=-0.4, warnings=["coda stazione elevata"], reasons=["coda elevata"]),
        AnalyzerSignal(module_name="components", order_id="C1", status="WARNING", priority_delta=-0.2, warnings=["shared component"], reasons=["componente condiviso in conflitto"]),
    ]
    res = merge_order_signals("C1", signals)
    assert res["merge_result"] in {"DEFER", "INVESTIGATE"}
    assert len(res["detected_conflicts"]) >= 1


def test_investigate_when_signals_are_weak():
    signals = [
        AnalyzerSignal(module_name="noop", order_id="D1", status="INFO", priority_delta=0.0),
    ]
    res = merge_order_signals("D1", signals)
    assert res["merge_result"] in {"ALLOW", "INVESTIGATE"}


def test_determinism_same_input_same_output():
    signals = [
        AnalyzerSignal(module_name="station", order_id="E1", status="OK", priority_delta=+0.1),
        AnalyzerSignal(module_name="priority", order_id="E1", status="OK", priority_delta=+0.2),
    ]
    a = merge_order_signals("E1", signals)
    b = merge_order_signals("E1", list(reversed(signals)))  # ordine invertito
    assert a == b

    merged = merge_all(signals)
    assert isinstance(merged, list) and merged[0]["order_id"] == "E1"

