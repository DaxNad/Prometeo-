from app.executor.schemas import ExecutionTask
from app.executor.tools.run_test_tool import run_test_tool


def _task(payload):
    return ExecutionTask(
        action="run_test",
        target_type="system",
        source="system",
        payload=payload,
    )


def test_run_test_tool_guarded_success():
    result = run_test_tool(
        _task(
            {
                "validation": {
                    "checks_required": [
                        "sequence_compat_check",
                        "machine_load",
                    ]
                }
            }
        )
    )
    assert result.success is True
    assert result.data["healthcheck"]["guard"] == "read_only"


def test_run_test_tool_fails_on_missing_checks():
    result = run_test_tool(_task({"validation": {"checks_required": ["machine_load"]}}))
    assert result.success is False
    assert result.error == "missing_required_checks"


def test_run_test_tool_fails_on_write_intent_marker():
    result = run_test_tool(
        _task(
            {
                "validation": {
                    "checks_required": ["sequence_compat_check", "machine_load"]
                },
                "intent": "write",
            }
        )
    )
    assert result.success is False
    assert result.error == "read_only_guard_violation"
