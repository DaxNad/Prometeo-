
from typing import Any
from app.executor.schemas import ExecutionTask


def build_execution_task(data: dict[str, Any]) -> ExecutionTask:
    """
    Converte qualsiasi input dict in ExecutionTask tipizzato.
    Protegge il boundary ATLAS → Executor.
    Gestisce sia formato flat (action="run_test") sia nested (action={"type": "run_test"}).
    """
    action_raw = data.get("action", "run_test")
    if isinstance(action_raw, dict):
        action = action_raw.get("type", "run_test")
    else:
        action = action_raw

    return ExecutionTask(
        action=action,
        target_type=data.get("target_type", "system"),
        target_id=data.get("target_id"),
        payload=data.get("payload", {}),
        source=data.get("source", "system"),
    )
