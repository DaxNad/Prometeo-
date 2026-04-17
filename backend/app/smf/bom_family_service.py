from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd


_COMPONENT_CODE_RE = re.compile(r"\b(?:\d{6}|[A-Z]{2,5}\d{3,4})\b")


def normalize_drawing(value: object) -> str:
    return str(value or "").strip().replace(" ", "")


def build_family_summary_by_drawing(
    *,
    drawing: str,
    specs: pd.DataFrame,
    components: pd.DataFrame,
    operations: pd.DataFrame,
    markings: pd.DataFrame,
    variants: pd.DataFrame,
) -> dict[str, Any]:
    target = normalize_drawing(drawing)
    family_specs = _collect_family_specs_by_drawing(specs, target)
    articoli = family_specs["articolo"].astype(str).tolist()

    comp_family = components[components["articolo"].astype(str).isin(articoli)]
    op_family = operations[operations["articolo"].astype(str).isin(articoli)]
    mark_family = markings[markings["articolo"].astype(str).isin(articoli)]
    var_family = variants[variants["articolo"].astype(str).isin(articoli)]

    componenti_unici = _collect_nested_component_codes(
        articoli=articoli,
        family_specs=family_specs,
        comp_family=comp_family,
        op_family=op_family,
    )
    fasi_uniche = _collect_fasi(op_family)
    postazioni_stimate = _estimate_postazioni(fasi_uniche)
    count_markings = len(mark_family.index)

    return {
        "ok": True,
        "drawing": drawing,
        "normalized_drawing": target,
        "articoli_famiglia": articoli,
        "count_articoli": len(articoli),
        "componenti_coinvolti": componenti_unici,
        "count_componenti": len(componenti_unici),
        "fasi_coinvolte": fasi_uniche,
        "postazioni_stimate": postazioni_stimate,
        "criticita_tl": _infer_criticita_tl(
            postazioni_stimate=postazioni_stimate,
            componenti_unici=componenti_unici,
        ),
        "rotazione": _infer_rotazione(
            articoli=articoli,
            componenti_unici=componenti_unici,
            fasi_uniche=fasi_uniche,
            count_markings=count_markings,
        ),
        "tassativo": _infer_tassativo(articoli, family_specs, var_family),
        "peso_turno": _build_peso_turno(
            postazioni_stimate=postazioni_stimate,
            count_markings=count_markings,
            count_componenti=len(componenti_unici),
            count_articoli=len(articoli),
        ),
        "tipo_famiglia": _infer_tipo_famiglia(articoli, family_specs),
        "raw": {
            "specs": family_specs.to_dict(orient="records"),
            "components": comp_family.to_dict(orient="records"),
            "operations": op_family.to_dict(orient="records"),
            "markings": mark_family.to_dict(orient="records"),
            "variants": var_family.to_dict(orient="records"),
        },
    }


def _collect_family_specs_by_drawing(specs: pd.DataFrame, target: str) -> pd.DataFrame:
    normalized_specs = specs["disegno"].astype(str).map(normalize_drawing)
    return specs[normalized_specs == target].copy()


def _safe_json_loads(value: object) -> object | None:
    if isinstance(value, (dict, list)):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _collect_component_codes(*values: object) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            for item in node.values():
                _walk(item)
            return
        if isinstance(node, list):
            for item in node:
                _walk(item)
            return
        text = str(node or "").upper()
        for match in _COMPONENT_CODE_RE.findall(text):
            if match not in seen:
                seen.add(match)
                matches.append(match)

    for value in values:
        parsed = _safe_json_loads(value)
        _walk(parsed if parsed is not None else value)

    return matches


def _append_unique(target: list[str], values: list[str], *, skip: set[str] | None = None) -> None:
    existing = set(target)
    ignored = skip or set()
    for value in values:
        if value in existing or value in ignored:
            continue
        target.append(value)
        existing.add(value)


def _collect_nested_component_codes(
    *,
    articoli: list[str],
    family_specs: pd.DataFrame,
    comp_family: pd.DataFrame,
    op_family: pd.DataFrame,
) -> list[str]:
    componenti_unici: list[str] = []
    articoli_set = {str(value).strip().upper() for value in articoli if str(value).strip()}

    direct_componenti = (
        comp_family["codice_componente"]
        .astype(str)
        .replace("", None)
        .dropna()
        .str.upper()
        .unique()
        .tolist()
    )
    _append_unique(componenti_unici, direct_componenti, skip=articoli_set)

    if "raw_json" in family_specs.columns:
        for raw in family_specs["raw_json"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(raw), skip=articoli_set)

    if "extra" in comp_family.columns:
        for extra in comp_family["extra"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(extra), skip=articoli_set)

    if "extra" in op_family.columns:
        for extra in op_family["extra"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(extra), skip=articoli_set)

    return componenti_unici


def _collect_fasi(op_family: pd.DataFrame) -> list[str]:
    return (
        op_family["fase"]
        .astype(str)
        .replace("", None)
        .dropna()
        .unique()
        .tolist()
    )


def _estimate_postazioni(fasi_uniche: list[str]) -> list[str]:
    postazioni_stimate: list[str] = []

    for fase in fasi_uniche:
        fase_upper = fase.upper()
        if "GUAINA" in fase_upper:
            postazioni_stimate.append("GUAINE")
        if "PIDMILL" in fase_upper:
            postazioni_stimate.append("PIDMILL")
        if "ZAW" in fase_upper:
            postazioni_stimate.append("ZAW")
        if "HENN" in fase_upper:
            postazioni_stimate.append("HENN")
        if "CP" in fase_upper or "COLLAUDO" in fase_upper:
            postazioni_stimate.append("CP")

    return sorted(set(postazioni_stimate))


def _infer_criticita_tl(
    *,
    postazioni_stimate: list[str],
    componenti_unici: list[str],
) -> list[str]:
    criticita: list[str] = []

    if "GUAINE" in postazioni_stimate:
        criticita.append("carico_guaina")
    if len(componenti_unici) > 4:
        criticita.append("multi_component")
    if "PIDMILL" in postazioni_stimate:
        criticita.append("tempo_pidmill")
    if "ZAW" in postazioni_stimate:
        criticita.append("tempo_zaw")

    return criticita


def _infer_tipo_famiglia(articoli: list[str], family_specs: pd.DataFrame) -> str:
    unique_articoli = {str(value).strip() for value in articoli if str(value).strip()}
    if len(unique_articoli) >= 3:
        return "famiglia_complessivo"
    family_markers = " ".join(
        family_specs.get("famiglia_processo", pd.Series(dtype=str)).astype(str).str.upper().tolist()
    )
    if "BASE" in family_markers and len(unique_articoli) == 1:
        return "lineare"
    return "famiglia"


def _infer_tassativo(
    articoli: list[str],
    family_specs: pd.DataFrame,
    var_family: pd.DataFrame,
) -> bool:
    payload = " ".join(
        family_specs.get("raw_json", pd.Series(dtype=str)).astype(str).tolist()
        + var_family.astype(str).agg(" ".join, axis=1).tolist()
        + articoli
    ).upper()
    has_partial = any(token in payload for token in ("PARZIALE", "PARTIAL"))
    has_group = any(token in payload for token in ("COMPLESSIVO", "COMPLESSIVI", "GRUPPO", "ASSIEME"))
    return has_partial and has_group


def _infer_rotazione(
    *,
    articoli: list[str],
    componenti_unici: list[str],
    fasi_uniche: list[str],
    count_markings: int,
) -> str:
    fase_tokens = " ".join(fasi_uniche).upper()
    fast_lane = not any(token in fase_tokens for token in ("PIDMILL", "HENN", "ZAW", "COLLAUDO", "CP"))
    single_linear = len(articoli) == 1 and len(componenti_unici) <= 2 and len(fasi_uniche) <= 3 and count_markings <= 1
    return "alta" if single_linear and fast_lane else "da_verificare"


def _build_peso_turno(
    *,
    postazioni_stimate: list[str],
    count_markings: int,
    count_componenti: int,
    count_articoli: int,
) -> dict[str, Any]:
    per_postazione: dict[str, int] = {}
    driver: list[str] = []
    totale = 1

    if "PIDMILL" in postazioni_stimate:
        per_postazione["PIDMILL"] = per_postazione.get("PIDMILL", 0) + 2
        driver.append("peso_pidmill")
        totale += 2
    if "HENN" in postazioni_stimate:
        per_postazione["HENN"] = per_postazione.get("HENN", 0) + 2
        driver.append("peso_henn")
        totale += 2
    if count_markings >= 2:
        driver.append("multi_marcatura")
        totale += 2
    if count_componenti > 4:
        driver.append("multi_component")
        totale += 1
    if count_articoli >= 3:
        driver.append("famiglia_ampia")
        totale += 1

    livello = "alto" if totale >= 5 else "medio" if totale >= 3 else "basso"
    return {
        "totale": totale,
        "livello": livello,
        "driver": driver,
        "per_postazione": per_postazione,
    }
