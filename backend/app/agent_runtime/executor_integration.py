
"""
Integration layer:

ATLAS decision → Executor
"""

from typing import Optional, Dict, Any

from app.executor.service import execute_task


def maybe_execute_task_from_atlas(decision_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Esegue executor solo se ATLAS produce un task.

    Non genera side effects sul dominio operativo.
    """

    task_data = decision_payload.get("executor_task")

    if not task_data:

        return None


    result = execute_task(task_data)

    return {

        "executor_result": result,

    }
