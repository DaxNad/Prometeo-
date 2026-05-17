"""CLI eval-only for sanitized TL semantic evals."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.tl_semantic_eval_runner import evaluate_case
DEFAULT_MATRIX_PATH = REPO_ROOT / "evals" / "fixtures" / "tl_semantic_eval_matrix_001.json"


def load_matrix(path: Path = DEFAULT_MATRIX_PATH) -> dict:
    return json.loads(path.read_text())


def run_eval(matrix: dict) -> tuple[bool, list[str]]:
    lines: list[str] = []
    all_passed = True

    lines.append("PROMETEO TL SEMANTIC EVAL")
    lines.append(f"matrix={matrix['eval_matrix_id']}")
    lines.append(f"state={matrix['state']}")
    lines.append("")

    for case in matrix["cases"]:
        result = evaluate_case(case["accepted_answer"], case)
        status = "PASS" if result.passed else "FAIL"

        if not result.passed:
            all_passed = False

        lines.append(f"{status} {case['case_id']}")
        matched = ",".join(result.matched_meanings) if result.matched_meanings else "-"
        missing = ",".join(result.missing_meanings) if result.missing_meanings else "-"
        lines.append(f"  matched={matched}")
        lines.append(f"  missing={missing}")

    lines.append("")
    lines.append(f"RESULT={'PASS' if all_passed else 'FAIL'}")

    return all_passed, lines


def main() -> int:
    matrix = load_matrix()
    passed, lines = run_eval(matrix)
    print("\n".join(lines))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
