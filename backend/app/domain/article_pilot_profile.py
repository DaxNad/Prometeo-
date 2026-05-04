from __future__ import annotations

import json
from typing import Any

import pandas as pd


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_json_loads(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    raw = _clean(value)
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    return parsed if isinstance(parsed, dict) else {}


def _rows_for_article(df: pd.DataFrame, article: str) -> pd.DataFrame:
    if "articolo" not in df.columns:
        return df.iloc[0:0]

    target = _clean(article).upper()
    return df[df["articolo"].astype(str).str.strip().str.upper() == target].copy()


def _extract_components_from_specs(raw_json: dict[str, Any]) -> list[str]:
    components: list[str] = []

    innesto = raw_json.get("innesto_rapido_1")
    if isinstance(innesto, dict):
        for item in innesto.get("componenti") or []:
            cleaned = _clean(item)
            if cleaned:
                components.append(cleaned)

    for item in raw_json.get("componenti") or []:
        if isinstance(item, dict):
            cleaned = _clean(item.get("codice"))
        else:
            cleaned = _clean(item)

        if cleaned:
            components.append(cleaned)

    return list(dict.fromkeys(components))


def _extract_tooling(raw_json: dict[str, Any]) -> list[str]:
    tooling: list[str] = []

    innesto = raw_json.get("innesto_rapido_1")
    if isinstance(innesto, dict):
        cleaned = _clean(innesto.get("attrezzatura"))
        if cleaned:
            tooling.append(cleaned)

    zaw_1 = raw_json.get("zaw_1")
    if isinstance(zaw_1, dict):
        cleaned = _clean(zaw_1.get("crm"))
        if cleaned:
            tooling.append(cleaned)

    return list(dict.fromkeys(tooling))


def _extract_packaging(raw_json: dict[str, Any]) -> dict[str, Any]:
    packaging = raw_json.get("packaging")
    if isinstance(packaging, dict):
        return {str(k): v for k, v in packaging.items()}

    return {}


def build_article_pilot_profile(
    article: str,
    *,
    specs: pd.DataFrame,
    operations: pd.DataFrame,
    controls: pd.DataFrame,
) -> dict[str, Any]:
    article_code = _clean(article)

    specs_rows = _rows_for_article(specs.fillna(""), article_code)
    operation_rows = _rows_for_article(operations.fillna(""), article_code)
    control_rows = _rows_for_article(controls.fillna(""), article_code)

    discrepancies: list[str] = []

    if specs_rows.empty:
        return {
            "ok": False,
            "article": article_code,
            "confidence": "DA_VERIFICARE",
            "discrepancies": ["missing_bom_specs"],
        }

    spec = specs_rows.iloc[0].to_dict()
    raw_json = _safe_json_loads(spec.get("raw_json"))

    raw_pattern = _clean(raw_json.get("pattern"))
    cluster_name = _clean(spec.get("cluster_name"))
    if raw_pattern and cluster_name and raw_pattern != cluster_name:
        discrepancies.append("pattern_cluster_mismatch")

    route_raw = []
    if "seq_no" in operation_rows.columns:
        operation_rows = operation_rows.sort_values(by=["seq_no"])

    for _, row in operation_rows.iterrows():
        fase = _clean(row.get("fase"))
        if fase:
            route_raw.append(fase)

    if not route_raw:
        sequence = raw_json.get("sequenza")
        if isinstance(sequence, list):
            route_raw = [_clean(item) for item in sequence if _clean(item)]

    if not route_raw:
        discrepancies.append("missing_route")

    controls_payload: dict[str, Any] = {}
    if not control_rows.empty:
        first_control = control_rows.iloc[0].to_dict()
        controls_payload = _safe_json_loads(first_control.get("extra"))

    confidence = "INFERITO"
    if not discrepancies:
        confidence = "CERTO"
    elif "missing_route" in discrepancies:
        confidence = "DA_VERIFICARE"

    return {
        "ok": True,
        "article": article_code,
        "sap_code": _clean(spec.get("codice_articolo")) or _clean(raw_json.get("codice_sap")),
        "drawing": _clean(spec.get("disegno")) or _clean(raw_json.get("disegno")),
        "revision": _clean(spec.get("rev")) or _clean(raw_json.get("documento", {}).get("rev") if isinstance(raw_json.get("documento"), dict) else ""),
        "qta_lotto": spec.get("qta_lotto"),
        "qta_imballo": spec.get("qta_imballo"),
        "codice_imballo": _clean(spec.get("codice_imballo")),
        "raw_pattern": raw_pattern,
        "cluster_name": cluster_name,
        "route_raw": route_raw,
        "components_from_specs": _extract_components_from_specs(raw_json),
        "tooling": _extract_tooling(raw_json),
        "packaging": _extract_packaging(raw_json),
        "controls": controls_payload,
        "cp_required": bool(spec.get("cp_required")) if str(spec.get("cp_required")).strip() else False,
        "confidence": confidence,
        "discrepancies": discrepancies,
        "source": "BOM_Specs+BOM_Operations+BOM_Controls",
    }
