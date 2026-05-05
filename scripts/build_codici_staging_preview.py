#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SMF_DIR = ROOT / "data" / "local_smf"
MASTER = SMF_DIR / "SuperMegaFile_Master.xlsx"
LIFECYCLE_REGISTRY = SMF_DIR / "article_lifecycle_registry.json"
OUTPUT = SMF_DIR / "codici_staging_preview.json"


def clean(value: Any) -> str:
    return str(value or "").strip()


def parse_raw(value: Any) -> dict[str, Any]:
    raw = clean(value)
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
    except Exception:
        return {}

    return parsed if isinstance(parsed, dict) else {}


def valid_revision(value: Any) -> bool:
    rev = clean(value)
    return bool(rev) and rev not in {"—", "-", "None", "none", "nan", "NAN"}


def looks_like_multi_drawing(value: str) -> bool:
    v = clean(value)
    return v.startswith("{") and v.endswith("}")


def load_lifecycle_registry() -> dict[str, dict[str, Any]]:
    if not LIFECYCLE_REGISTRY.exists():
        return {}

    try:
        data = json.loads(LIFECYCLE_REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for code, payload in data.items():
        if isinstance(payload, dict):
            out[str(code).strip().upper()] = payload

    return out


def next_action_from_lifecycle(status: str) -> str:
    normalized = clean(status).upper()

    if normalized == "NEW_ENTRY":
        return "REVIEW_HIGH_PRIORITY"
    if normalized == "FUORI_PRODUZIONE":
        return "DO_NOT_STAGE"
    if normalized == "DA_VERIFICARE":
        return "TL_REVIEW_REQUIRED"

    return "REVIEW_BEFORE_STAGING"


def build_staging_preview() -> dict[str, Any]:
    if not MASTER.exists():
        return {
            "ok": False,
            "error": "SuperMegaFile_Master.xlsx not found",
            "output": str(OUTPUT),
            "items": [],
            "excluded": [],
        }

    codici = pd.read_excel(MASTER, sheet_name="Codici").fillna("")
    specs = pd.read_excel(MASTER, sheet_name="BOM_Specs").fillna("")
    operations = pd.read_excel(MASTER, sheet_name="BOM_Operations").fillna("")

    lifecycle = load_lifecycle_registry()

    codici_set = {
        str(v).strip().upper()
        for v in codici.get("Codice", pd.Series(dtype=str)).tolist()
        if str(v).strip()
    }

    items: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for _, row in specs.iterrows():
        articolo = clean(row.get("articolo"))
        if not articolo or articolo.upper() in codici_set:
            continue

        raw_json = parse_raw(row.get("raw_json"))
        documento = raw_json.get("documento") if isinstance(raw_json.get("documento"), dict) else {}

        disegno = clean(row.get("disegno")) or clean(raw_json.get("disegno"))
        rev = clean(row.get("rev")) or clean(documento.get("rev"))
        cluster = clean(row.get("cluster_name"))
        pattern = clean(raw_json.get("pattern"))
        codice_sap = clean(row.get("codice_articolo")) or clean(raw_json.get("codice_sap"))
        qta_imballo = clean(row.get("qta_imballo")) or clean(documento.get("qta_imballo"))
        codice_imballo = clean(row.get("codice_imballo")) or clean(documento.get("imballo_codice"))

        article_ops = (
            operations[operations["articolo"].astype(str).str.strip() == articolo]
            if "articolo" in operations.columns
            else pd.DataFrame()
        )

        lifecycle_payload = lifecycle.get(articolo.upper(), {})
        lifecycle_status = clean(lifecycle_payload.get("status")) or "SCONOSCIUTO"
        lifecycle_source = clean(lifecycle_payload.get("source"))
        lifecycle_note = clean(lifecycle_payload.get("note"))

        issues: list[str] = []
        if not disegno or disegno in {"None", "none", "nan"}:
            issues.append("missing_drawing")
        if looks_like_multi_drawing(disegno):
            issues.append("multi_drawing")
        if not valid_revision(rev):
            issues.append("missing_revision")
        if article_ops.empty:
            issues.append("missing_operations")
        if lifecycle_status == "DA_VERIFICARE":
            issues.append("lifecycle_da_verificare")
        if lifecycle_status == "FUORI_PRODUZIONE":
            issues.append("lifecycle_fuori_produzione")

        base = {
            "codice": articolo,
            "descrizione": f"Articolo {articolo} - {disegno}",
            "tipo": "DA_CLASSIFICARE",
            "revisione": rev,
            "disegno": disegno,
            "imballo": codice_imballo,
            "codice_sap": codice_sap,
            "cluster": cluster,
            "pattern": pattern,
            "qta_imballo": qta_imballo,
            "operations_count": int(len(article_ops)),
            "lifecycle_status": lifecycle_status,
            "lifecycle_source": lifecycle_source,
            "lifecycle_note": lifecycle_note,
            "tl_decision": "PENDING",
            "next_action": next_action_from_lifecycle(lifecycle_status),
            "staging_status": "PREVIEW_ONLY",
        }

        if issues:
            excluded.append({**base, "issues": issues})
            continue

        items.append(base)

    return {
        "ok": True,
        "mode": "CODICI_STAGING_PREVIEW_V1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "master": str(MASTER),
        "output": str(OUTPUT),
        "summary": {
            "items_ready_for_tl_review": len(items),
            "excluded_or_blocked": len(excluded),
            "writes_to_smf": 0,
            "writes_to_db": 0,
        },
        "items": items,
        "excluded": excluded,
    }


def main() -> int:
    payload = build_staging_preview()

    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("# CODICI STAGING PREVIEW")
    print()
    print(f"ok: {payload.get('ok')}")
    print(f"mode: {payload.get('mode')}")
    print(f"output: {OUTPUT}")
    print(f"items_ready_for_tl_review: {payload.get('summary', {}).get('items_ready_for_tl_review')}")
    print(f"excluded_or_blocked: {payload.get('summary', {}).get('excluded_or_blocked')}")
    print("writes_to_smf: 0")
    print("writes_to_db: 0")

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
