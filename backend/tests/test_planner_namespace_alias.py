from fastapi.testclient import TestClient

import app.api_production as api_production
from app.main import app


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

    prod_sequence = client.get("/production/sequence")
    planner_sequence = client.get("/planner/sequence")
    assert prod_sequence.status_code == 200
    assert planner_sequence.status_code == 200
    assert planner_sequence.json() == prod_sequence.json()

    prod_turn_plan = client.get("/production/turn-plan")
    planner_turn_plan = client.get("/planner/turn-plan")
    assert prod_turn_plan.status_code == 200
    assert planner_turn_plan.status_code == 200
    assert planner_turn_plan.json() == prod_turn_plan.json()

    prod_explain = client.get("/production/explain")
    planner_explain = client.get("/planner/explain")
    assert prod_explain.status_code == 200
    assert planner_explain.status_code == 200
    assert planner_explain.json() == prod_explain.json()
