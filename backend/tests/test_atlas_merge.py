from app.services.atlas_merge import merge_atlas_v1


def test_blocking_wins():
    payload = merge_atlas_v1(
        [
            {
                "module": "constraint_guard",
                "outcome": "BLOCK",
                "score": 0.95,
                "reasons": ["hard safety stop"],
                "active_constraints": ["BLOCKING_SAFETY"],
            },
            {
                "module": "flow_optimizer",
                "outcome": "PROCEED",
                "score": 0.90,
                "reasons": ["lead time gain"],
                "active_constraints": [],
            },
        ]
    )

    assert payload["final_outcome"] == "BLOCK"
    assert "BLOCKING_SAFETY" in payload["active_constraints"]


def test_conflicting_modules():
    payload = merge_atlas_v1(
        [
            {
                "module": "module_a",
                "outcome": "PROCEED",
                "score": 0.70,
                "reasons": ["ok"],
                "active_constraints": [],
            },
            {
                "module": "module_b",
                "outcome": "REVIEW",
                "score": 0.70,
                "reasons": ["risk"],
                "active_constraints": [],
            },
        ]
    )

    assert payload["final_outcome"] in {"REVIEW", "MONITOR", "PROCEED"}
    assert payload["conflicts"]


def test_positive_convergence():
    payload = merge_atlas_v1(
        [
            {
                "module": "capacity",
                "outcome": "PROCEED",
                "score": 0.80,
                "reasons": ["capacity free"],
                "active_constraints": [],
            },
            {
                "module": "priority",
                "outcome": "PROCEED",
                "score": 0.75,
                "reasons": ["high customer priority"],
                "active_constraints": [],
            },
        ]
    )

    assert payload["final_outcome"] == "PROCEED"
    assert payload["final_score"] >= 0.55


def test_empty_weak_signals_fallback():
    payload = merge_atlas_v1([])
    assert payload["final_outcome"] == "MONITOR"
    assert payload["final_score"] == 0.0


def test_output_schema_stability():
    payload = merge_atlas_v1(
        [
            {
                "module": "schema_check",
                "outcome": "MONITOR",
                "score": 0.40,
                "reasons": ["weak signal"],
                "active_constraints": [],
            }
        ]
    )

    assert set(payload.keys()) == {
        "final_outcome",
        "final_score",
        "reasons",
        "active_constraints",
        "conflicts",
        "consensus",
        "explain_brief",
    }
