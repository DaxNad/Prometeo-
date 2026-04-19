
from typing import Any
from app.executor.schemas import ExecutionTask


def build_execution_task(data: dict[str, Any]) -> ExecutionTask:
    """
    Converte qualsiasi input dict in ExecutionTask tipizzato.
    Protegge il boundary ATLAS → Executor.
    """

    return ExecutionTask(

        action=data.get("action", "run_test"),

        target_type=data.get("target_type", "system"),

        target_id=data.get("target_id"),

        payload=data.get("payload", {}),

        source=data.get("source", "system"),

        safety_level=data.get("safety_level", "low"),

        explain=data.get("explain"),

    )
