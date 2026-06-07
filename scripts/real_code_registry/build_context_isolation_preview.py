#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts/real_code_registry/build_real_code_registry_preview.py"
REGISTRY_JSON = Path(
    os.environ.get(
        "PROMETEO_REAL_CODE_REGISTRY_OUT_DIR",
        ROOT / "data/local_reports/real_code_registry",
    )
) / "real_code_registry_preview.json"


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


def build_contexts(record: dict | None, code: str) -> dict:
    if record is None:
        return {
            "found": False,
            "mode": "preview_only",
            "code": code,
            "article_context": {
                "code": code,
                "known": False,
                "confidence": "UNKNOWN",
                "route_status": "UNKNOWN",
                "planner_safe": False,
            },
            "spec_context": {
                "sources": [],
                "evidence_refs": [],
                "process_signals": {},
                "contradictions": [],
            },
            "turn_context": {
                "tl_required": True,
                "safe_answer_mode": "OBSERVATIONAL_ONLY",
                "requires_confirmation": True,
            },
            "deploy_context": {
                "writes_to_planner": False,
                "writes_to_smf": False,
                "writes_to_db": False,
                "uses_backend_runtime": False,
                "uses_ai_runtime": False,
            },
            "guard": {
                "planner_allowed": False,
                "response_allowed": True,
                "reason": "missing_registry_record",
            },
        }

    pack = record.get("evidence_pack") or {}

    return {
        "found": True,
        "mode": "preview_only",
        "code": str(record.get("code")),
        "article_context": {
            "code": str(record.get("code")),
            "known": True,
            "confidence": record.get("confidence"),
            "route_status": record.get("route_status"),
            "planner_safe": False,
            "evidence_score": record.get("evidence_score"),
            "sources": record.get("sources") or [],
        },
        "spec_context": {
            "sources": record.get("sources") or [],
            "evidence_refs": record.get("evidence_refs") or [],
            "process_signals": pack.get("process_signals") or {},
            "contradictions": record.get("contradictions") or [],
            "contradiction_summary": pack.get("contradiction_summary") or [],
            "missing_fields": pack.get("missing_fields") or [],
        },
        "turn_context": {
            "tl_required": pack.get("tl_required") is True,
            "safe_answer_mode": "OBSERVATIONAL_ONLY",
            "requires_confirmation": pack.get("tl_required") is True or bool(record.get("contradictions")),
        },
        "deploy_context": {
            "writes_to_planner": False,
            "writes_to_smf": False,
            "writes_to_db": False,
            "uses_backend_runtime": False,
            "uses_ai_runtime": False,
        },
        "guard": {
            "planner_allowed": False,
            "response_allowed": True,
            "reason": "context_isolation_preview_only",
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: build_context_isolation_preview.py <5-digit-code>", file=sys.stderr)
        return 2

    code = argv[1].strip()
    if not (code.isdigit() and len(code) == 5):
        print("ERROR: code must be a 5-digit numeric value", file=sys.stderr)
        return 2

    data = load_registry()
    record = find_record(data, code)
    result = build_contexts(record, code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if record is not None else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
