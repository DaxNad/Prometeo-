from app.executor.schemas import CertaintyLevel


def _normalize_certainty(value) -> CertaintyLevel:
    if value in {"CERTO", "INFERITO", "DA_VERIFICARE"}:
        return value
    return "DA_VERIFICARE"


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

    data = execution.get("data", {})
    classification = data.get("classification", {}) if isinstance(data, dict) else {}
    certainty = _normalize_certainty(classification.get("certainty"))
    result = classification.get("result")
    reasons = classification.get("reasons", [])

    if result == "MATCH":
        return {
            "outcome": "SUCCESS",
            "certainty": certainty,
            "reasons": reasons if isinstance(reasons, list) else [],
            "warnings": [],
        }

    if result == "PARTIAL_MATCH":
        return {
            "outcome": "SUCCESS",
            "certainty": certainty,
            "reasons": reasons if isinstance(reasons, list) else [],
            "warnings": ["crosscheck_partial_match"],
        }

    if result == "MISMATCH":
        return {
            "outcome": "FAILED",
            "certainty": certainty,
            "reasons": reasons if isinstance(reasons, list) else ["bom_mismatch"],
            "warnings": [],
        }

    return {
        "outcome": "SUCCESS",
        "certainty": "INFERITO",
        "reasons": [],
        "warnings": [],
    }
