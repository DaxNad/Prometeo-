from __future__ import annotations

from typing import Any

from app.executor.schemas import ExecutionResult, ExecutionTask, CertaintyLevel


_CLASSIFICATION = {
    "CERTO": "MATCH",
    "INFERITO": "PARTIAL_MATCH",
    "DA_VERIFICARE": "MISMATCH",
}


def _to_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {
        str(item).strip()
        for item in value
        if str(item).strip()
    }


def _extract_bucket(section: dict[str, Any], key: str) -> set[str]:
    return _to_string_set(section.get(key, []))


def _compare_bucket(expected: set[str], observed: set[str]) -> dict[str, Any]:
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    overlap = sorted(expected & observed)
    expected_size = len(expected)
    match_ratio = 0.0 if expected_size == 0 else round(len(overlap) / expected_size, 3)

    return {
        "expected": sorted(expected),
        "observed": sorted(observed),
        "missing": missing,
        "unexpected": unexpected,
        "overlap": overlap,
        "match_ratio": match_ratio,
    }


def _infer_certainty(comparison: dict[str, dict[str, Any]]) -> tuple[CertaintyLevel, list[str]]:
    if not comparison:
        return "DA_VERIFICARE", ["missing_comparison_scope"]

    total_expected = sum(len(bucket["expected"]) for bucket in comparison.values())
    total_missing = sum(len(bucket["missing"]) for bucket in comparison.values())
    total_unexpected = sum(len(bucket["unexpected"]) for bucket in comparison.values())
    total_overlap = sum(len(bucket["overlap"]) for bucket in comparison.values())

    reasons: list[str] = []

    if total_expected == 0:
        reasons.append("missing_expected_reference")
        return "DA_VERIFICARE", reasons

    if total_missing == 0 and total_unexpected == 0 and total_overlap > 0:
        reasons.append("full_structured_match")
        return "CERTO", reasons

    if total_overlap > 0:
        reasons.append("partial_overlap_detected")
        if total_missing > 0:
            reasons.append("expected_items_missing")
        if total_unexpected > 0:
            reasons.append("unexpected_items_detected")
        return "INFERITO", reasons

    reasons.append("no_overlap_detected")
    return "DA_VERIFICARE", reasons


def crosscheck_bom_tool(task: ExecutionTask) -> ExecutionResult:
    payload = task.payload if isinstance(task.payload, dict) else {}
    expected = payload.get("expected", {})
    observed = payload.get("observed", {})

    if not isinstance(expected, dict) or not isinstance(observed, dict):
        return ExecutionResult(
            success=False,
            error="invalid_payload_sections",
            data={},
        )

    compare_keys = ("components", "operations")
    comparison: dict[str, dict[str, Any]] = {}

    for key in compare_keys:
        expected_bucket = _extract_bucket(expected, key)
        observed_bucket = _extract_bucket(observed, key)
        if expected_bucket or observed_bucket:
            comparison[key] = _compare_bucket(expected_bucket, observed_bucket)

    certainty, reasons = _infer_certainty(comparison)

    return ExecutionResult(
        success=True,
        data={
            "mode": "read_only_crosscheck",
            "comparison": comparison,
            "classification": {
                "certainty": certainty,
                "result": _CLASSIFICATION[certainty],
                "reasons": reasons,
            },
        },
    )
