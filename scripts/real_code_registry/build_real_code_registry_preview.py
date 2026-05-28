#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data/local_reports/real_code_registry"
OUT_JSON = OUT_DIR / "real_code_registry_preview.json"
OUT_SUMMARY = OUT_DIR / "real_code_registry_summary.md"

SCAN_DIRS = [
    ROOT / "data/local_reports/runtime_pilot",
    ROOT / "data/local_reports",
]

CODE_RE = re.compile(r"\b\d{5}\b")

TECHNICAL_NUMBERS_BLACKLIST = {
    "11434",  # Ollama port
    "8000",   # FastAPI dev port
    "5432",   # PostgreSQL
    "99999",  # sentinel / fake value
}

HIGH_SIGNAL_HINTS = {
    "article",
    "articolo",
    "codice",
    "metadata",
    "runtime",
    "spec",
    "specifica",
    "smf",
    "route",
    "zaw",
    "henn",
    "pidmill",
    "cp",
}

def source_name(path: Path) -> str:
    ptxt = str(path)
    if "runtime_pilot" in ptxt:
        return "RUNTIME_PILOT_NOTES"
    return "LOCAL_REPORTS"

def signal_quality(text: str) -> str:
    lower = text.lower()
    hits = sum(1 for h in HIGH_SIGNAL_HINTS if h in lower)
    if hits >= 3:
        return "HIGH"
    if hits >= 1:
        return "MEDIUM"
    return "LOW"

def scan_codes() -> tuple[dict[str, dict], list[dict]]:
    records: dict[str, dict] = {}
    excluded_candidates: list[dict] = []

    for directory in SCAN_DIRS:
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt", ".json", ".csv"}:
                continue
            if "real_code_registry" in str(path):
                continue

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            sq = signal_quality(text)

            for code in sorted(set(CODE_RE.findall(text))):
                ref = str(path.relative_to(ROOT))

                if code in TECHNICAL_NUMBERS_BLACKLIST:
                    excluded_candidates.append({
                        "value": code,
                        "classification": "TECHNICAL_NUMBER",
                        "signal_quality": sq,
                        "registry_action": "EXCLUDE",
                        "exclusion_reason": "TECHNICAL_NUMBERS_BLACKLIST",
                        "source_file": ref,
                    })
                    continue

                rec = records.setdefault(code, {
                    "code": code,
                    "sources": [],
                    "confidence": "DA_VERIFICARE",
                    "observed_in_field": True,
                    "route_status": "UNKNOWN",
                    "planner_safe": False,
                    "evidence_count": 0,
                    "contradictions": [],
                    "last_seen": date.today().isoformat(),
                    "signal_quality": sq,
                    "exclusion_reason": None,
                    "evidence_refs": [],
                })

                src = source_name(path)
                if src not in rec["sources"]:
                    rec["sources"].append(src)

                if ref not in rec["evidence_refs"]:
                    rec["evidence_refs"].append(ref)
                    rec["evidence_count"] += 1

                current = rec.get("signal_quality", "LOW")
                rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                if rank[sq] > rank[current]:
                    rec["signal_quality"] = sq

    return records, excluded_candidates

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records, excluded_candidates = scan_codes()

    unique_excluded = []
    seen_excluded = set()
    for item in excluded_candidates:
        key = (
            item.get("value"),
            item.get("classification"),
            item.get("source_file"),
            item.get("exclusion_reason"),
        )
        if key in seen_excluded:
            continue
        seen_excluded.add(key)
        unique_excluded.append(item)

    registry = {
        "capability": "010_REAL_CODE_REGISTRY",
        "mode": "preview_only",
        "generated_at": date.today().isoformat(),
        "rules": {
            "planner_safe_default": False,
            "writes_to_planner": False,
            "writes_to_smf": False,
            "writes_to_db": False,
            "promotes_to_certo": False,
        },
        "records": [records[k] for k in sorted(records)],
        "excluded_candidates": unique_excluded,
    }

    OUT_JSON.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    OUT_SUMMARY.write_text(
        "# REAL_CODE_REGISTRY — preview summary\n\n"
        "Mode: preview_only\n\n"
        f"Records: {len(records)}\n"
        f"Excluded candidates: {len(excluded_candidates)}\n\n"
        "Planner writes: false\n"
        "SMF writes: false\n"
        "DB writes: false\n"
        "Auto-promotion to CERTO: false\n\n"
        "## Codes\n\n"
        + "\n".join(f"- {code}" for code in sorted(records))
        + ("\n" if records else ""),
        encoding="utf-8",
    )

    print(f"WROTE {OUT_JSON}")
    print(f"WROTE {OUT_SUMMARY}")
    print(f"RECORDS {len(records)}")
    print(f"EXCLUDED {len(unique_excluded)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
