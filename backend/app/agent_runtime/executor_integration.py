
"""
Integration layer:

ATLAS decision → Executor
"""

from typing import Optional, Dict, Any

from app.executor.service import execute_task


def _is_explicit_executor_allow(decision_payload: Dict[str, Any]) -> bool:
    if decision_payload.get("executor_allowed") is True:
        return True

    executor_meta = decision_payload.get("executor")
    if isinstance(executor_meta, dict) and executor_meta.get("allow") is True:
        return True

    decision = decision_payload.get("decision")
    if isinstance(decision, dict):
        if decision.get("executor_allowed") is True:
            return True
        compatibility = str(decision.get("executor_compatibility", "")).strip().upper()
        if compatibility in {"ALLOW", "ALLOWED", "COMPATIBLE"}:
            return True

    return False


def _is_blocked_or_deferred(decision_payload: Dict[str, Any]) -> bool:
    decision = decision_payload.get("decision")
    candidates: list[str] = []

    for key in ("status", "outcome", "decision", "action", "decision_mode"):
        if key in decision_payload:
            candidates.append(str(decision_payload.get(key, "")))

    if isinstance(decision, dict):
        for key in ("status", "outcome", "decision", "action", "decision_mode"):
            if key in decision:
                candidates.append(str(decision.get(key, "")))

    normalized = " ".join(candidates).strip().lower()
    if not normalized:
        return False

    blocked_tokens = ("blocked", "block", "deferred", "defer")
    return any(token in normalized for token in blocked_tokens)


def maybe_execute_task_from_atlas(decision_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Esegue executor solo se ATLAS produce un task.

    Non genera side effects sul dominio operativo.
    """

    task_data = decision_payload.get("executor_task")

    if not task_data:

        return None

    if _is_blocked_or_deferred(decision_payload) and not _is_explicit_executor_allow(decision_payload):
        return None

    result = execute_task(task_data)

    return {

        "executor_result": result,

    }
