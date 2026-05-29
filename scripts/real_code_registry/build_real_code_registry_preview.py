#!/usr/bin/env python3
from __future__ import annotations

import csv
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

def apply_bom_specs(records: dict[str, dict]) -> None:
    bom = ROOT / "data/local_smf/BOM_Specs.csv"
    if not bom.exists():
        return

    with bom.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("articolo") or "").strip()
            if not CODE_RE.fullmatch(code):
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
                "signal_quality": "HIGH",
                "exclusion_reason": None,
                "evidence_refs": [],
            })

            if "SMF_BOM_SPECS" not in rec["sources"]:
                rec["sources"].append("SMF_BOM_SPECS")

            ref = "data/local_smf/BOM_Specs.csv"
            if ref not in rec["evidence_refs"]:
                rec["evidence_refs"].append(ref)
                rec["evidence_count"] += 1

            rec["smf_bom_specs_seen"] = True
            rec["smf_famiglia_processo"] = (row.get("famiglia_processo") or "").strip() or None
            rec["smf_documento_tipo"] = (row.get("documento_tipo") or "").strip() or None
            rec["smf_disegno"] = (row.get("disegno") or "").strip() or None
            rec["smf_codice_imballo"] = (row.get("codice_imballo") or "").strip() or None

            # Guardrail: BOM_Specs is observational here only.
            rec["planner_safe"] = False
            rec["confidence"] = rec.get("confidence") or "DA_VERIFICARE"
            rec["route_status"] = rec.get("route_status") or "UNKNOWN"

def apply_tl_real_spec_intake(records: dict[str, dict]) -> None:
    src = ROOT / "data/local_reports/tl_real_spec_intake/TL_REAL_SPEC_INTAKE_001.json"
    if not src.exists():
        return

    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except Exception:
        return

    if data.get("planner_auto_allowed") is not False:
        return
    if data.get("database_write_allowed") is not False:
        return
    if data.get("smf_write_allowed") is not False:
        return
    if data.get("git_versioning_allowed") is not False:
        return

    ref = str(src.relative_to(ROOT))

    for item in data.get("items", []):
        code = str(item.get("article") or "").strip()
        if not CODE_RE.fullmatch(code):
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
            "signal_quality": "HIGH",
            "exclusion_reason": None,
            "evidence_refs": [],
        })

        if "TL_REAL_SPEC_INTAKE" not in rec["sources"]:
            rec["sources"].append("TL_REAL_SPEC_INTAKE")

        if ref not in rec["evidence_refs"]:
            rec["evidence_refs"].append(ref)
            rec["evidence_count"] += 1

        rec["tl_real_spec_intake_seen"] = True
        rec["tl_real_spec_initial_classification"] = item.get("initial_classification")
        rec["tl_real_spec_visible_processes"] = item.get("visible_processes") or []
        rec["tl_real_spec_visible_components"] = item.get("visible_components") or []
        rec["tl_real_spec_drawing"] = item.get("drawing")
        rec["tl_real_spec_sap_code"] = item.get("sap_code")

        # Guardrail: real spec intake is still observational here.
        rec["planner_safe"] = False
        rec["confidence"] = rec.get("confidence") or "DA_VERIFICARE"
        rec["route_status"] = rec.get("route_status") or "UNKNOWN"

KNOWN_OBSERVATIONAL_MISMATCH_RULES = {
    "12056": {
        "kind": "KNOWN_ROUTE_SOURCE_LIMITATION",
        "severity": "MEDIUM",
        "reason": "BOM/spec-derived route may underrepresent TL-confirmed PIDMILL/CP flow for 12056.",
    },
    "12058": {
        "kind": "KNOWN_ZAW_RESOLUTION_RISK",
        "severity": "HIGH",
        "reason": "SMF_BOM_SPECS may indicate PIDMILL_ZAW2, but 12058 requires TL-sensitive ZAW resolution and must remain non-planner-safe.",
    },
    "12511": {
        "kind": "KNOWN_ZAW2_FALSE_INFERENCE_RISK",
        "severity": "HIGH",
        "reason": "12511 has double ZAW1 known behavior; do not infer physical ZAW2 from double tooling/pass signals.",
    },
}

def apply_known_contradiction_rules(records: dict[str, dict]) -> None:
    for code, rule in KNOWN_OBSERVATIONAL_MISMATCH_RULES.items():
        rec = records.get(code)
        if not rec:
            continue

        existing = {
            (
                c.get("kind"),
                c.get("severity"),
                c.get("reason"),
            )
            for c in rec.get("contradictions", [])
            if isinstance(c, dict)
        }

        item = {
            "kind": rule["kind"],
            "severity": rule["severity"],
            "reason": rule["reason"],
            "status": "OBSERVATIONAL_ONLY",
            "planner_blocking": True,
        }

        key = (item["kind"], item["severity"], item["reason"])
        if key not in existing:
            rec.setdefault("contradictions", []).append(item)

        rec["planner_safe"] = False
        rec["route_status"] = "DA_VERIFICARE"


def build_contradiction_explainability(item: dict) -> dict:
    return {
        "rule": item.get("kind") or "UNKNOWN_CONTRADICTION",
        "severity": item.get("severity") or "UNKNOWN",
        "status": item.get("status") or "OBSERVATIONAL_ONLY",
        "field": item.get("field") or "route_or_process_consistency",
        "source_context": item.get("source_context") or "REGISTRY_PREVIEW",
        "observed": item.get("observed") or item.get("reason") or "source mismatch or known source limitation",
        "expected": item.get("expected") or "TL-confirmed or stronger source alignment",
        "impact": item.get("impact") or "route_confidence_degraded",
        "operator_action": item.get("operator_action") or "TL review required before planner-safe use",
    }


def apply_contradiction_explainability(records: dict[str, dict]) -> None:
    for rec in records.values():
        for item in rec.get("contradictions") or []:
            if isinstance(item, dict):
                item["explainability"] = build_contradiction_explainability(item)


PROCESS_SIGNAL_ALIASES = {
    "ZAW1": {"ZAW1", "ZAW-1"},
    "ZAW2": {"ZAW2", "ZAW-2"},
    "HENN": {"HENN"},
    "PIDMILL": {"PIDMILL"},
    "CP": {"CP", "COLLAUDO_A_PRESSIONE", "COLLAUDO_PRESSIONE", "COLLAUDO_VERTICALE"},
}


def _has_signal(value: object, aliases: set[str]) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        text = " ".join(str(v) for v in value)
    else:
        text = str(value)
    upper = text.upper()
    return any(alias in upper for alias in aliases)


def _source_signals(rec: dict) -> dict[str, set[str]]:
    signals: dict[str, set[str]] = {}

    smf_family = rec.get("smf_famiglia_processo")
    if smf_family:
        for signal, aliases in PROCESS_SIGNAL_ALIASES.items():
            if _has_signal(smf_family, aliases):
                signals.setdefault("SMF_BOM_SPECS", set()).add(signal)

    tl_processes = rec.get("tl_real_spec_visible_processes") or []
    if tl_processes:
        for signal, aliases in PROCESS_SIGNAL_ALIASES.items():
            if _has_signal(tl_processes, aliases):
                signals.setdefault("TL_REAL_SPEC_INTAKE", set()).add(signal)

    return signals


def _append_cross_source_contradiction(rec: dict, item: dict) -> None:
    existing = {
        (
            c.get("kind"),
            c.get("source_a"),
            c.get("source_b"),
            c.get("signal"),
            c.get("reason"),
        )
        for c in rec.get("contradictions", [])
        if isinstance(c, dict)
    }
    key = (
        item.get("kind"),
        item.get("source_a"),
        item.get("source_b"),
        item.get("signal"),
        item.get("reason"),
    )
    if key not in existing:
        rec.setdefault("contradictions", []).append(item)

    rec["planner_safe"] = False
    rec["route_status"] = "DA_VERIFICARE"


def apply_cross_source_contradiction_detector(records: dict[str, dict]) -> None:
    for rec in records.values():
        signals = _source_signals(rec)
        smf = signals.get("SMF_BOM_SPECS", set())
        tl = signals.get("TL_REAL_SPEC_INTAKE", set())

        if not smf or not tl:
            continue

        if "ZAW2" in smf and "ZAW1" in tl and "ZAW2" not in tl:
            _append_cross_source_contradiction(rec, {
                "kind": "ZAW_STATION_MISMATCH",
                "severity": "HIGH",
                "source_a": "SMF_BOM_SPECS",
                "source_b": "TL_REAL_SPEC_INTAKE",
                "signal": "ZAW",
                "reason": "SMF_BOM_SPECS indicates ZAW2 while TL_REAL_SPEC_INTAKE indicates ZAW1 without ZAW2.",
                "status": "OBSERVATIONAL_ONLY",
                "planner_blocking": True,
            })

        if "PIDMILL" in smf and "PIDMILL" not in tl:
            _append_cross_source_contradiction(rec, {
                "kind": "PIDMILL_SIGNAL_MISMATCH",
                "severity": "MEDIUM",
                "source_a": "SMF_BOM_SPECS",
                "source_b": "TL_REAL_SPEC_INTAKE",
                "signal": "PIDMILL",
                "reason": "SMF_BOM_SPECS indicates PIDMILL while TL_REAL_SPEC_INTAKE does not expose PIDMILL.",
                "status": "OBSERVATIONAL_ONLY",
                "planner_blocking": True,
            })

        if "HENN" in smf and "HENN" not in tl:
            _append_cross_source_contradiction(rec, {
                "kind": "HENN_SIGNAL_MISMATCH",
                "severity": "MEDIUM",
                "source_a": "SMF_BOM_SPECS",
                "source_b": "TL_REAL_SPEC_INTAKE",
                "signal": "HENN",
                "reason": "SMF_BOM_SPECS indicates HENN while TL_REAL_SPEC_INTAKE does not expose HENN.",
                "status": "OBSERVATIONAL_ONLY",
                "planner_blocking": True,
            })

def apply_evidence_score(records: dict[str, dict]) -> None:
    for rec in records.values():
        sources = rec.get("sources", [])
        evidence_count = int(rec.get("evidence_count") or 0)
        contradictions = rec.get("contradictions", [])

        score = evidence_count + len(sources)
        if rec.get("smf_bom_specs_seen"):
            score += 2
        if rec.get("tl_real_spec_intake_seen"):
            score += 3
        if contradictions:
            score -= 2

        rec["evidence_score"] = max(score, 0)

def build_evidence_pack(rec: dict) -> dict:
    sources = rec.get("sources") or []
    evidence_refs = rec.get("evidence_refs") or []
    contradictions = rec.get("contradictions") or []
    signals = _source_signals(rec)

    source_summary = [
        {
            "source": source,
            "seen": True,
        }
        for source in sources
    ]

    process_signals = {
        "sources": {source: sorted(values) for source, values in signals.items()},
        "observed": sorted({value for values in signals.values() for value in values}),
    }

    contradiction_summary = [
        {
            "kind": item.get("kind"),
            "severity": item.get("severity"),
            "planner_blocking": item.get("planner_blocking", False),
        }
        for item in contradictions
        if isinstance(item, dict)
    ]

    missing_fields = []
    if not sources:
        missing_fields.append("sources")
    if not evidence_refs:
        missing_fields.append("evidence_refs")
    if rec.get("route_status") in {None, "UNKNOWN"}:
        missing_fields.append("confirmed_route")

    strict_input_ready = bool(rec.get("code") and sources and evidence_refs)
    has_strong_source = bool(rec.get("smf_bom_specs_seen") or rec.get("tl_real_spec_intake_seen"))

    return {
        "context_type": "REGISTRY_EVIDENCE_PACK",
        "strict_input_ready": strict_input_ready,
        "planner_allowed": False,
        "safe_answer_mode": "OBSERVATIONAL_ONLY",
        "source_summary": source_summary,
        "process_signals": process_signals,
        "contradiction_summary": contradiction_summary,
        "missing_fields": missing_fields,
        "tl_required": bool(contradictions or not has_strong_source or rec.get("route_status") != "CERTO"),
    }


def apply_evidence_pack(records: dict[str, dict]) -> None:
    for rec in records.values():
        rec["evidence_pack"] = build_evidence_pack(rec)

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

    apply_bom_specs(records)
    apply_tl_real_spec_intake(records)
    apply_known_contradiction_rules(records)
    apply_cross_source_contradiction_detector(records)
    apply_contradiction_explainability(records)
    apply_evidence_score(records)
    apply_evidence_pack(records)
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
