from app.agent_mod.quality_gate import run_quality_gate


def test_quality_gate_local_smoke():
    # Skip invoking pytest from within pytest to avoid recursion
    res = run_quality_gate(run_pytest=False)
    assert res["quality_gate"] == "PASS"
    checks = res["checks"]
    assert checks["health"] is True
    assert checks["smf_status"] is True
    assert checks["parse_single"] is True
    assert checks["parse_batch"] is True
