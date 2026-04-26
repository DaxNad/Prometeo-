from fastapi.testclient import TestClient

import app.api_production as api_production
from app.main import app


def strip_planner_addons(payload: dict) -> dict:
    return {
        k: v
        for k, v in payload.items()
        if k not in {"decision", "decision_trace"}
    }


def test_planner_namespace_matches_production(monkeypatch):
    monkeypatch.setattr(api_production, "trigger_runtime_analysis", lambda **kwargs: None)

    monkeypatch.setattr(
        api_production.sequence_planner_service,
        "build_global_sequence",
        lambda db: {
            "planner_stage": "TEST_SEQUENCE",
            "source_view": "vw_test_sequence",
            "items_count": 1,
            "items": [{"order_id": "ORD-1", "station": "ZAW-1", "priority": "ALTA"}],
        },
    )

    monkeypatch.setattr(
        api_production.sequence_planner_service,
        "build_turn_plan",
        lambda db: {
            "planner_stage": "TEST_TURN_PLAN",
            "source": "vw_test_turn_plan",
            "plan_date": "2026-04-22",
            "rotation_logic": "test_rotation",
            "clusters_count": 1,
            "assignments_count": 1,
            "assignments": [{"station": "ZAW-1", "order_id": "ORD-1"}],
        },
    )

    monkeypatch.setattr(
        api_production,
        "build_tl_explanation",
        lambda item: {
            "priority_reason": "test_reason",
            "risk_level": "LOW",
            "signals": {},
        },
    )

    client = TestClient(app)
    headers = {"X-API-Key": "PROMETEO_STRONG_KEY_2026"}

    prod_sequence = client.get("/production/sequence", headers=headers)
    planner_sequence = client.get("/planner/sequence", headers=headers)
    assert prod_sequence.status_code == 200
    assert planner_sequence.status_code == 200
    planner_sequence_body = planner_sequence.json()
    production_sequence_body = prod_sequence.json()
    assert "decision" in planner_sequence_body
    assert "decision_trace" in planner_sequence_body
    assert "decision" not in production_sequence_body
    assert "decision_trace" not in production_sequence_body
    assert strip_planner_addons(planner_sequence_body) == production_sequence_body

    prod_turn_plan = client.get("/production/turn-plan", headers=headers)
    planner_turn_plan = client.get("/planner/turn-plan", headers=headers)
    assert prod_turn_plan.status_code == 200
    assert planner_turn_plan.status_code == 200
    planner_turn_plan_body = planner_turn_plan.json()
    production_turn_plan_body = prod_turn_plan.json()
    assert "decision" in planner_turn_plan_body
    assert "decision_trace" in planner_turn_plan_body
    assert "decision" not in production_turn_plan_body
    assert "decision_trace" not in production_turn_plan_body
    assert strip_planner_addons(planner_turn_plan_body) == production_turn_plan_body

    prod_explain = client.get("/production/explain", headers=headers)
    planner_explain = client.get("/planner/explain", headers=headers)
    assert prod_explain.status_code == 200
    assert planner_explain.status_code == 200
    planner_explain_body = planner_explain.json()
    production_explain_body = prod_explain.json()
    assert "decision" in planner_explain_body
    assert "decision_trace" in planner_explain_body
    assert "decision" not in production_explain_body
    assert "decision_trace" not in production_explain_body
    assert strip_planner_addons(planner_explain_body) == production_explain_body
