import app.agent_runtime.executor_integration as integration


def test_executor_denied_without_explicit_decision_context(monkeypatch):
    called = {"value": False}

    def _forbidden_execute(_task):
        called["value"] = True
        return {"ok": True}

    monkeypatch.setattr(integration, "execute_task", _forbidden_execute)

    result = integration.maybe_execute_task_from_atlas(
        {
            "executor_task": {"action": "run_test"},
        }
    )

    assert result is None
    assert called["value"] is False


def test_executor_blocked_or_deferred_requires_explicit_allow(monkeypatch):
    called = {"value": False}

    def _forbidden_execute(_task):
        called["value"] = True
        return {"ok": True}

    monkeypatch.setattr(integration, "execute_task", _forbidden_execute)

    blocked = integration.maybe_execute_task_from_atlas(
        {
            "status": "BLOCKED",
            "executor_task": {"action": "run_test"},
        }
    )
    deferred = integration.maybe_execute_task_from_atlas(
        {
            "decision": {"status": "DEFER"},
            "executor_task": {"action": "run_test"},
        }
    )

    assert blocked is None
    assert deferred is None
    assert called["value"] is False


def test_executor_runs_when_context_explicit_and_allowed(monkeypatch):
    monkeypatch.setattr(integration, "execute_task", lambda _task: {"ok": True})

    result = integration.maybe_execute_task_from_atlas(
        {
            "status": "BLOCKED",
            "executor_allowed": True,
            "executor_task": {"action": "run_test"},
        }
    )

    assert result == {"executor_result": {"ok": True}}
