import os

from app.agent_mod.db_schema_guard import run_db_schema_guard


def test_db_schema_guard_handles_missing_database_url(monkeypatch):
    # Ensure we simulate an environment without DATABASE_URL
    monkeypatch.delenv("DATABASE_URL", raising=False)

    res = run_db_schema_guard()
    # Must not crash and must return FAIL with a reason
    assert isinstance(res, dict)
    assert res.get("db_schema_guard") == "FAIL"
    assert "backend" in res
    assert "checks" in res and isinstance(res["checks"], dict)
    assert "missing_tables" in res and isinstance(res["missing_tables"], list)
    assert "missing_views" in res and isinstance(res["missing_views"], list)
    assert "reason" in res  # explicit diagnostic

