from app.executor.schemas import ExecutionTask, ExecutionResult


def run_test_tool(task: ExecutionTask) -> ExecutionResult:
    payload = task.payload if isinstance(task.payload, dict) else {}

    checks_required = payload.get("checks_required")
    if not isinstance(checks_required, list):
        validation_payload = payload.get("validation", {})
        if isinstance(validation_payload, dict):
            checks_required = validation_payload.get("checks_required", [])
        else:
            checks_required = []

    checks_normalized = {
        str(check).strip()
        for check in checks_required
        if str(check).strip()
    }

    expected_checks = {"sequence_compat_check", "machine_load"}
    missing_checks = sorted(expected_checks - checks_normalized)

    if missing_checks:
        return ExecutionResult(
            success=False,
            error="missing_required_checks",
            data={
                "missing_checks": missing_checks,
            },
        )

    forbidden_write_markers = ("write", "mutate", "insert", "update", "delete")
    payload_blob = str(payload).lower()
    if any(marker in payload_blob for marker in forbidden_write_markers):
        return ExecutionResult(
            success=False,
            error="read_only_guard_violation",
            data={},
        )

    return ExecutionResult(
        success=True,
        data={
            "message": "executor_test_ok",
            "healthcheck": {
                "checks": sorted(expected_checks),
                "guard": "read_only",
            },
        },
    )
