#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCAL_ASSIST = REPO_ROOT / "tools" / "local_assist" / "local_assist.py"


CASES = [
    {
        "name": "dummy_neutral",
        "provider": "dummy",
        "input": "Output generico non classificabile.",
        "expected_verdict": "DA_VERIFICARE",
        "expected_risk": "MEDIUM",
    },
    {
        "name": "deterministic_checks_ok",
        "provider": "dummy",
        "input": "All checks were successful\n0 failing\n11 successful",
        "expected_verdict": "PASS",
        "expected_risk": "LOW",
    },
    {
        "name": "deterministic_data_leak_failed",
        "provider": "dummy",
        "input": "Some checks were not successful\nX Data Leak Guard\n2 failing",
        "expected_verdict": "FAIL",
        "expected_risk": "HIGH",
    },
    {
        "name": "unknown_provider_fails_closed",
        "provider": "unknown",
        "input": "Output generico non classificabile.",
        "expected_verdict": "DA_VERIFICARE",
        "expected_risk": "HIGH",
    },
]


def run_case(case: dict) -> dict:
    input_path = Path("/tmp") / f"prometeo_local_assist_eval_{case['name']}.txt"
    input_path.write_text(case["input"], encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(LOCAL_ASSIST),
            "--task",
            f"eval case {case['name']}",
            "--provider",
            case["provider"],
            "--input-file",
            str(input_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=80,
    )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {
            "verdict": "DA_VERIFICARE",
            "risk": "HIGH",
            "summary": "Output non JSON",
            "suggested_next_command": None,
            "requires_human_confirmation": True,
        }

    passed = (
        result.returncode == 0
        and output.get("verdict") == case["expected_verdict"]
        and output.get("risk") == case["expected_risk"]
        and output.get("requires_human_confirmation") is True
    )

    return {
        "name": case["name"],
        "provider": case["provider"],
        "passed": passed,
        "returncode": result.returncode,
        "expected": {
            "verdict": case["expected_verdict"],
            "risk": case["expected_risk"],
        },
        "actual": {
            "verdict": output.get("verdict"),
            "risk": output.get("risk"),
            "requires_human_confirmation": output.get("requires_human_confirmation"),
            "summary": output.get("summary"),
        },
        "stderr": result.stderr.strip(),
    }


def main() -> int:
    results = [run_case(case) for case in CASES]
    all_passed = all(item["passed"] for item in results)

    report = {
        "capability": "LOCAL_ASSIST_BRIDGE_003_EVAL",
        "verdict": "PASS" if all_passed else "FAIL",
        "cases": results,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
