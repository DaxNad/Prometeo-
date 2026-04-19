
from datetime import datetime, timezone


def map_execution_event(task, validation, execution, verification):

    return {

        "event_domain": "TECHNICAL",

        "event_type": "executor_task_processed",

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "task_action": getattr(task, "action", None),

        "task_target_type": getattr(task, "target_type", None),

        "task_target_id": getattr(task, "target_id", None),

        "task_source": getattr(task, "source", None),

        "validation_status": validation.get("status"),

        "execution_success": None if execution is None else execution.get("success"),

        "verification_outcome": verification.get("outcome"),

        "certainty": verification.get("certainty"),

        "reasons": verification.get("reasons", []),

        "warnings": verification.get("warnings", []),

    }
