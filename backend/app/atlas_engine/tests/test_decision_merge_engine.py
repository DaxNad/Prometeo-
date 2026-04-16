from app.atlas_engine.decision_merge_engine import (
    MergeInput,
    MergeSignal,
    solve_decision_merge,
)


def test_block_overrides_allow():
    result = solve_decision_merge(
        MergeInput(
            component_availability_result=MergeSignal(
                decision="BLOCK",
                reasons=["component shortage"],
            ),
            shipment_priority_result=MergeSignal(
                decision="ALLOW",
                score=0.9,
                reasons=["customer priority accepted"],
            ),
        )
    )

    assert result.decision == "BLOCK"
    assert result.priority_score == 0.0
    assert "component_availability: component shortage" in result.active_constraints


def test_defer_overrides_allow():
    result = solve_decision_merge(
        MergeInput(
            bottleneck_pressure_result=MergeSignal(
                decision="DEFER",
                reasons=["line saturation"],
                confidence=0.8,
            ),
            phase_progress_result=MergeSignal(
                decision="ALLOW",
                score=0.9,
                reasons=["phase aligned"],
            ),
        )
    )

    assert result.decision == "DEFER"
    assert 0.0 < result.priority_score < 0.5
    assert "bottleneck_pressure: line saturation" in result.active_constraints


def test_boost_increases_priority_score():
    allow_result = solve_decision_merge(
        MergeInput(
            shipment_priority_result=MergeSignal(
                decision="ALLOW",
                score=0.62,
                reasons=["priority confirmed"],
            )
        )
    )
    boost_result = solve_decision_merge(
        MergeInput(
            shipment_priority_result=MergeSignal(
                decision="BOOST",
                score=0.62,
                reasons=["urgent shipment"],
            )
        )
    )

    assert allow_result.decision == "ALLOW"
    assert boost_result.decision == "BOOST"
    assert boost_result.priority_score > allow_result.priority_score


def test_conflict_detection():
    result = solve_decision_merge(
        MergeInput(
            bottleneck_pressure_result=MergeSignal(
                decision="DEFER",
                reasons=["downstream bottleneck"],
            ),
            shipment_priority_result=MergeSignal(
                decision="BOOST",
                reasons=["premium customer"],
            ),
        )
    )

    assert result.decision == "DEFER"
    assert result.conflicts == [
        "bottleneck_pressure:DEFER conflicts with shipment_priority:BOOST"
    ]


def test_explain_contains_constraints():
    result = solve_decision_merge(
        MergeInput(
            operator_capacity_result=MergeSignal(
                decision="BLOCK",
                reasons=["missing certified operator"],
            ),
            shipment_priority_result=MergeSignal(
                decision="BOOST",
                reasons=["expedite requested"],
            ),
        )
    )

    assert "missing certified operator" in result.explain
    assert "operator_capacity" in result.explain

