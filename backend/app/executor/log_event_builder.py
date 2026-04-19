
def build_executor_log_event(event: dict) -> dict:

    event_domain = event.get("event_domain", "TECHNICAL")

    return {

        "title": f"Executor event: {event.get('event_type')}",

        "line": "SYSTEM",

        "station": "EXECUTOR",

        "event_type": event.get("event_type"),

        "severity": "LOW" if event.get("verification_outcome") == "SUCCESS" else "MEDIUM",

        "status": "OPEN",

        "note": str({

            "event_domain": event_domain,

            "task_action": event.get("task_action"),

            "task_target_type": event.get("task_target_type"),

            "task_target_id": event.get("task_target_id"),

            "task_source": event.get("task_source"),

            "validation_status": event.get("validation_status"),

            "execution_success": event.get("execution_success"),

            "verification_outcome": event.get("verification_outcome"),

            "certainty": event.get("certainty"),

            "reasons": event.get("reasons", []),

            "warnings": event.get("warnings", []),

            "timestamp": event.get("timestamp"),

        }),

    }
