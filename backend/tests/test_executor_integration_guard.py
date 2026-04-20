import app.agent_runtime.executor_integration as integration


def test_executor_integration_skips_blocked_without_explicit_allow(monkeypatch):
    called = {"value": False}

    def _fake_execute_task(_):
        called["value"] = True
        return {"ok": True}

    monkeypatch.setattr(integration, "execute_task", _fake_execute_task)

    result = integration.maybe_execute_task_from_atlas(
        {
            "status": "BLOCKED",
            "executor_task": {"action": "run_test"},
        }
    )
    assert result is None
    assert called["value"] is False


def test_executor_integration_allows_blocked_when_explicitly_allowed(monkeypatch):
    monkeypatch.setattr(integration, "execute_task", lambda _: {"ok": True})

    result = integration.maybe_execute_task_from_atlas(
        {
            "status": "DEFERRED",
            "executor_allowed": True,
            "executor_task": {"action": "run_test"},
        }
    )
    assert result == {"executor_result": {"ok": True}}


def test_executor_integration_executes_non_blocked_task(monkeypatch):
    monkeypatch.setattr(integration, "execute_task", lambda _: {"ok": True})

    result = integration.maybe_execute_task_from_atlas(
        {
            "status": "ALLOW",
            "executor_task": {"action": "run_test"},
        }
    )
    assert result == {"executor_result": {"ok": True}}
