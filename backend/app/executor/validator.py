from app.executor.schemas import ExecutionTask


ALLOWED_ACTIONS = {"run_test", "crosscheck_bom"}
ALLOWED_SOURCES = {"system"}


def validate_task(task: ExecutionTask) -> dict:
    reasons = []

    if task.action not in ALLOWED_ACTIONS:
        reasons.append("action_not_allowed")

    if task.source not in ALLOWED_SOURCES:
        reasons.append("source_not_allowed")

    if reasons:
        return {
            "allowed": False,
            "status": "BLOCK",
            "reasons": reasons,
        }

    return {
        "allowed": True,
        "status": "ALLOW",
        "reasons": [],
    }
