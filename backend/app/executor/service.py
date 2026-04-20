
from app.executor.schemas import ExecutionTask
from app.executor.validator import validate_task
from app.executor.registry import TOOLS
from app.executor.verifier import verify_execution_result
from app.executor.event_mapper import map_execution_event
from app.executor.log_event_builder import build_executor_log_event
from app.executor.task_factory import build_execution_task


def execute_task(task_input) -> dict:

    if isinstance(task_input, dict):
        task = build_execution_task(task_input)
    else:
        task = task_input


    validation = validate_task(task)

    if not validation["allowed"]:

        verification = verify_execution_result(None)

        event = map_execution_event(
            task,
            validation,
            None,
            verification,
        )

        log_event = build_executor_log_event(event)

        return {
            "validation": validation,
            "execution": None,
            "verification": verification,
            "event": event,
            "log_event": log_event,
        }


    tool = TOOLS.get(task.action)

    if tool is None:

        execution = {
            "success": False,
            "error": "tool_not_found",
            "data": {},
        }

        verification = verify_execution_result(execution)

        event = map_execution_event(
            task,
            validation,
            execution,
            verification,
        )

        log_event = build_executor_log_event(event)

        return {
            "validation": validation,
            "execution": execution,
            "verification": verification,
            "event": event,
            "log_event": log_event,
        }


    result = tool(task)

    execution = result.model_dump()

    verification = verify_execution_result(execution)

    event = map_execution_event(
        task,
        validation,
        execution,
        verification,
    )

    log_event = build_executor_log_event(event)

    return {
        "validation": validation,
        "execution": execution,
        "verification": verification,
        "event": event,
        "log_event": log_event,
    }
