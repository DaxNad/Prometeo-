from app.agent_mod.schema_guard import run_schema_guard


def test_schema_guard_smoke():
    res = run_schema_guard()
    assert res["schema_guard"] == "PASS"
    checks = res["checks"]
    assert checks["health_schema"] is True
    assert checks["smf_status_schema"] is True
    assert checks["parse_single_schema"] is True
    assert checks["parse_batch_schema"] is True
