from app.agent_mod.quality_gate import _extract_pytest_failure_detail, run_quality_gate


def test_quality_gate_local_smoke():
    # Skip invoking pytest from within pytest to avoid recursion
    res = run_quality_gate(run_pytest=False)
    assert res["quality_gate"] == "PASS"
    checks = res["checks"]
    assert checks["health"] is True
    assert checks["smf_status"] is True
    assert checks["parse_single"] is True
    assert checks["parse_batch"] is True


def test_quality_gate_pytest_failure_detail_prefers_failed_tests():
    stdout = """
=========================== short test summary info ============================
FAILED backend/tests/test_example.py::test_example - AssertionError: expected true
FAILED backend/tests/test_other.py::test_other - RuntimeError: broken
4 failed, 611 passed, 3 deselected, 1 warning in 6.42s
"""
    detail = _extract_pytest_failure_detail(stdout=stdout, stderr="")

    assert detail.startswith("pytest failed tests:")
    assert "backend/tests/test_example.py::test_example" in detail
    assert "backend/tests/test_other.py::test_other" in detail
