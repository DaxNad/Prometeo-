#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts/real_code_registry/build_real_code_registry_preview.py"
REGISTRY_JSON = ROOT / "data/local_reports/real_code_registry/real_code_registry_preview.json"


def ensure_preview_exists() -> None:
    subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def load_registry() -> dict:
    ensure_preview_exists()
    return json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))


def find_record(data: dict, code: str) -> dict | None:
    for record in data.get("records", []):
        if str(record.get("code")) == code:
            return record
    return None


def compact_record(record: dict) -> dict:
    pack = record.get("evidence_pack") or {}
    return {
        "code": record.get("code"),
        "confidence": record.get("confidence"),
        "route_status": record.get("route_status"),
        "planner_safe": record.get("planner_safe"),
        "sources": record.get("sources") or [],
        "evidence_refs": record.get("evidence_refs") or [],
        "evidence_score": record.get("evidence_score"),
        "process_signals": pack.get("process_signals") or {},
        "contradictions": record.get("contradictions") or [],
        "tl_required": pack.get("tl_required"),
        "strict_input_ready": pack.get("strict_input_ready"),
        "safe_answer_mode": pack.get("safe_answer_mode"),
        "planner_allowed": pack.get("planner_allowed"),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: query_registry_evidence_pack.py <5-digit-code>", file=sys.stderr)
        return 2

    code = argv[1].strip()
    if not (code.isdigit() and len(code) == 5):
        print("ERROR: code must be a 5-digit numeric value", file=sys.stderr)
        return 2

    data = load_registry()
    record = find_record(data, code)
    if record is None:
        print(json.dumps({
            "found": False,
            "code": code,
            "mode": "preview_only",
            "planner_allowed": False,
            "safe_answer_mode": "OBSERVATIONAL_ONLY",
        }, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({
        "found": True,
        "mode": "preview_only",
        "record": compact_record(record),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
