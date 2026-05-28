#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
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


def summarize(data: dict) -> dict:
    records = data.get("records", [])

    contradicted = [
        record for record in records
        if record.get("contradictions")
    ]

    tl_required = [
        record for record in records
        if (record.get("evidence_pack") or {}).get("tl_required") is True
    ]

    not_strict_input_ready = [
        record for record in records
        if (record.get("evidence_pack") or {}).get("strict_input_ready") is not True
    ]

    contradiction_counter: Counter[str] = Counter()
    for record in contradicted:
        for item in record.get("contradictions") or []:
            if isinstance(item, dict):
                contradiction_counter[item.get("kind") or "UNKNOWN"] += 1

    return {
        "mode": "preview_only",
        "planner_allowed": False,
        "safe_answer_mode": "OBSERVATIONAL_ONLY",
        "records_total": len(records),
        "contradicted_records": len(contradicted),
        "tl_required_records": len(tl_required),
        "not_strict_input_ready": len(not_strict_input_ready),
        "top_contradictions": [
            {"kind": kind, "count": count}
            for kind, count in contradiction_counter.most_common()
        ],
        "codes_requiring_tl": sorted(
            str(record.get("code"))
            for record in tl_required
            if record.get("code")
        ),
        "codes_contradicted": sorted(
            str(record.get("code"))
            for record in contradicted
            if record.get("code")
        ),
    }


def main() -> int:
    data = load_registry()
    print(json.dumps(summarize(data), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
