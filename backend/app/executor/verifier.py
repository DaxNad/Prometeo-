def verify_execution_result(execution: dict) -> dict:
    if not execution:
        return {
            "outcome": "BLOCKED",
            "certainty": "DA_VERIFICARE",
            "reasons": ["missing_execution"],
            "warnings": [],
        }

    if execution.get("success") is not True:
        return {
            "outcome": "FAILED",
            "certainty": "DA_VERIFICARE",
            "reasons": [execution.get("error", "unknown_error")],
            "warnings": [],
        }

    return {
        "outcome": "SUCCESS",
        "certainty": "INFERITO",
        "reasons": [],
        "warnings": [],
    }
