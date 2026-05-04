#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "local_smf" / "SuperMegaFile_Master.xlsx"


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


def build_preview() -> tuple[pd.DataFrame, pd.DataFrame]:
    codici = pd.read_excel(MASTER, sheet_name="Codici").fillna("")
    specs = pd.read_excel(MASTER, sheet_name="BOM_Specs").fillna("")
    operations = pd.read_excel(MASTER, sheet_name="BOM_Operations").fillna("")

    codici_set = {
        str(v).strip().upper()
        for v in codici.get("Codice", pd.Series(dtype=str)).tolist()
        if str(v).strip()
    }

    candidate_rows: list[dict[str, Any]] = []
    excluded_rows: list[dict[str, Any]] = []

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

        issues: list[str] = []
        if not disegno or disegno in {"None", "none", "nan"}:
            issues.append("missing_drawing")
        if looks_like_multi_drawing(disegno):
            issues.append("multi_drawing")
        if not valid_revision(rev):
            issues.append("missing_revision")
        if article_ops.empty:
            issues.append("missing_operations")

        base = {
            "Codice": articolo,
            "Descrizione": f"Articolo {articolo} - {disegno}",
            "Categoria (Europa1/Europa2/America/AMG)": "",
            "Tipo (singolo/complessivo/sintetico)": "DA_CLASSIFICARE",
            "Cliente": "",
            "Revisione": rev,
            "Disegno associato (link)": disegno,
            "Imballo": codice_imballo,
            "Note": (
                f"PREVIEW_DA_BOM; codice_sap={codice_sap}; "
                f"cluster={cluster}; pattern={pattern}; "
                f"qta_imballo={qta_imballo}; ops={len(article_ops)}"
            ),
        }

        if issues:
            excluded = dict(base)
            excluded["issues"] = ",".join(issues)
            excluded_rows.append(excluded)
            continue

        candidate_rows.append(base)

    return pd.DataFrame(candidate_rows), pd.DataFrame(excluded_rows)


def main() -> int:
    print("# PREVIEW CODICI DA BOM — READ-ONLY")
    print()
    print(f"Master: {MASTER}")

    if not MASTER.exists():
        print("ERRORE: SuperMegaFile_Master.xlsx non trovato")
        return 1

    candidates, excluded = build_preview()

    print(f"Righe candidate solide: {len(candidates)}")
    print(f"Righe escluse/da verificare: {len(excluded)}")
    print()

    if not candidates.empty:
        print("## CANDIDATI SOLIDI")
        print(candidates.to_string(index=False))
        print()

    if not excluded.empty:
        print("## ESCLUSI / DA VERIFICARE")
        cols = ["Codice", "Revisione", "Disegno associato (link)", "Imballo", "issues"]
        available = [c for c in cols if c in excluded.columns]
        print(excluded[available].to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
