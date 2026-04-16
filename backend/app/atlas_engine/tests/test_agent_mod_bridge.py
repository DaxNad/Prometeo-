from app.atlas_engine.agent_mod.agent_mod_bridge import run_agent_mod_bridge
from app.atlas_engine.agent_mod.post_rank_explainer import enrich_merge_result
from app.atlas_engine.agent_mod.pre_rank_guard import run_pre_rank_guard
from app.atlas_engine.agent_mod.signal_normalizer import normalize_raw_signals
from app.atlas_engine.decision_merge_engine import MergeResult, MergeSignal


def test_signal_normalizer_normalizes_raw_payload():
    normalized = normalize_raw_signals(
        {
            "shipment_priority_result": {
                "decision": "boost",
                "score": 1.4,
                "confidence": 2.0,
                "reason": "expedite",
            },
            "line_capacity": {
                "status": "warning",
                "reasons": ["tight capacity"],
            },
        }
    )

    assert normalized == [
        MergeSignal(
            decision="BOOST",
            score=1.0,
            confidence=1.0,
            reasons=["expedite"],
            source_module="shipment_priority",
        ),
        MergeSignal(
            decision="DEFER",
            score=None,
            confidence=None,
            reasons=["tight capacity"],
            source_module="line_capacity",
        ),
    ]


def test_pre_rank_guard_blocks_conflicting_duplicate_module_decisions():
    guard_result = run_pre_rank_guard(
        [
            MergeSignal(decision="ALLOW", source_module="line_capacity"),
            MergeSignal(decision="BLOCK", source_module="line_capacity"),
        ]
    )

    assert guard_result.hard_block is not None
    assert guard_result.hard_block.decision == "BLOCK"
    assert guard_result.hard_block.active_constraints == [
        "pre_rank_guard: incoherent signal set: line_capacity"
    ]


def test_post_rank_explainer_reports_alignment():
    explained = enrich_merge_result(
        MergeResult(
            decision="DEFER",
            priority_score=0.3,
            active_constraints=["bottleneck_pressure: line saturation"],
            conflicts=["bottleneck_pressure:DEFER conflicts with shipment_priority:BOOST"],
            explain="DEFER by explicit constraint precedence.",
        ),
        normalized_signals=[
            MergeSignal(
                decision="DEFER",
                reasons=["line saturation"],
                source_module="bottleneck_pressure",
            ),
            MergeSignal(
                decision="BOOST",
                reasons=["premium customer"],
                source_module="shipment_priority",
            ),
        ],
    )

    assert explained.explain_short == "DEFER: bottleneck_pressure: line saturation"
    assert explained.agreeing_modules == ["bottleneck_pressure"]
    assert explained.disagreeing_modules == ["shipment_priority"]


def test_agent_mod_bridge_runs_end_to_end():
    result = run_agent_mod_bridge(
        {
            "component_availability_result": {"decision": "neutral"},
            "line_capacity_result": {"decision": "neutral"},
            "shipment_priority_result": {
                "decision": "boost",
                "reason": "premium shipment",
            },
            "bottleneck_pressure_result": {
                "decision": "defer",
                "reason": "line saturation",
            },
            "phase_progress_result": {"decision": "neutral"},
            "operator_capacity_result": {"decision": "allow", "reason": "crew ready"},
        }
    )

    assert result.decision == "DEFER"
    assert result.main_reasons[0] == "bottleneck_pressure: line saturation"
    assert result.agreeing_modules == ["bottleneck_pressure"]
    assert result.disagreeing_modules == ["shipment_priority", "operator_capacity"]
