#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_DIR = REPO_ROOT / "evals" / "prometeo_pilot_cases"
REQUIRED_FIELDS = {
    "id",
    "title",
    "question",
    "input_scope",
    "expected_constraints",
    "forbidden_outputs",
    "sample_output",
}


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    passed: bool
    failures: tuple[str, ...]


def main() -> int:
    args = _parse_args()
    cases = _load_cases(Path(args.cases_dir))

    if not cases:
        print("PROMETEO evals: nessun caso trovato.")
        return 1

    results = [_evaluate_case(case) for case in cases]
    passed = sum(1 for result in results if result.passed)

    print("PROMETEO synthetic eval harness")
    print(f"Cases: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    print("")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.case_id}")
        for failure in result.failures:
            print(f"  - {failure}")

    return 0 if all(result.passed for result in results) else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run synthetic PROMETEO pilot eval contracts."
    )
    parser.add_argument(
        "--cases-dir",
        default=str(DEFAULT_CASES_DIR),
        help="Directory containing synthetic eval case JSON files.",
    )
    return parser.parse_args()


def _load_cases(cases_dir: Path) -> list[dict]:
    if not cases_dir.exists():
        return []

    cases: list[dict] = []
    for path in sorted(cases_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["_path"] = path.as_posix()
        cases.append(payload)
    return cases


def _evaluate_case(case: dict) -> EvalResult:
    failures: list[str] = []
    missing_fields = sorted(REQUIRED_FIELDS - set(case))
    if missing_fields:
        failures.append(f"missing_fields={','.join(missing_fields)}")

    if case.get("input_scope") != "synthetic":
        failures.append("input_scope_must_be_synthetic")

    sample_output = str(case.get("sample_output", "")).lower()
    for expected in case.get("expected_constraints", []) or []:
        if str(expected).lower() not in sample_output:
            failures.append(f"missing_expected_constraint={expected}")

    for forbidden in case.get("forbidden_outputs", []) or []:
        if str(forbidden).lower() in sample_output:
            failures.append(f"forbidden_output_present={forbidden}")

    return EvalResult(
        case_id=str(case.get("id") or case.get("_path") or "unknown_case"),
        passed=not failures,
        failures=tuple(failures),
    )


if __name__ == "__main__":
    raise SystemExit(main())
