from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd
from app.domain.drawing_registry_service import (
    get_drawing_behavior as get_registry_behavior,
)


_COMPONENT_CODE_RE = re.compile(r"\b(?:\d{6}|[A-Z]{2,5}\d{3,4})\b")


def _collect_fasi(op_family: pd.DataFrame) -> list[str]:
    return (
        op_family["fase"]
        .astype(str)
        .replace("", None)
        .dropna()
        .unique()
        .tolist()
    )



def normalize_drawing(value: object) -> str:
    return str(value or "").strip().replace(" ", "")


def _load_registry_for_drawing(drawing: str) -> dict | None:
    return get_registry_behavior(drawing)


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

    registry_entry = _load_registry_for_drawing(target)

    family_specs = _collect_family_specs_by_drawing(specs, target)

    articoli = family_specs["articolo"].astype(str).tolist()

    articoli_unici = [
        str(value).strip()
        for value in articoli
        if str(value).strip()
    ]

    comp_family = components[
        components["articolo"].astype(str).isin(articoli)
    ]

    op_family = operations[
        operations["articolo"].astype(str).isin(articoli)
    ]

    mark_family = markings[
        markings["articolo"].astype(str).isin(articoli)
    ]

    var_family = variants[
        variants["articolo"].astype(str).isin(articoli)
    ]

    componenti_unici = _collect_nested_component_codes(
        articoli=articoli,
        family_specs=family_specs,
        comp_family=comp_family,
        op_family=op_family,
    )

    fasi_uniche = _collect_fasi(op_family)

    postazioni_stimate = _estimate_postazioni(fasi_uniche)

    registry_override = False

    if registry_entry:

        stations_registry = registry_entry.get("stations")

        if stations_registry:

            postazioni_stimate = stations_registry
            registry_override = True

    count_markings = len(mark_family.index)

    classificazione_per_articolo = _build_classificazione_per_articolo(
        articoli=articoli_unici,
        family_specs=family_specs,
        var_family=var_family,
    )

    family_has_complessivo = any(
        value in {"complessivo", "parziale_di_complessivo"}
        for value in classificazione_per_articolo.values()
    )

    quota_complessivo = (
        len(set(articoli_unici))
        if family_has_complessivo
        and len(set(articoli_unici)) > 1
        else None
    )

    dipendenza_parziale = _build_dipendenza_parziale(
        classificazione_per_articolo=classificazione_per_articolo,
        quota_per_complessivo=quota_complessivo,
    )

    quota_per_complessivo = {

        articolo:
        quota_complessivo
        if dipendenza_parziale.get(articolo, False)
        else None

        for articolo in articoli_unici
    }

    confidence = _build_confidence_summary(
        postazioni_stimate=postazioni_stimate,
        registry_override=registry_override,
    )

    discrepancy_flags = _build_discrepancy_flags(
        postazioni_stimate=postazioni_stimate,
        registry_override=registry_override,
    )

    return {

        "ok": True,

        "drawing": drawing,

        "normalized_drawing": target,

        "registry_applied": registry_override,

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

        "rotazione": (
            registry_entry.get("rotation")
            if registry_entry and registry_entry.get("rotation")
            else _infer_rotazione(
                articoli=articoli,
                componenti_unici=componenti_unici,
                fasi_uniche=fasi_uniche,
                count_markings=count_markings,
            )
        ),

        "tassativo": _infer_tassativo(
            articoli,
            family_specs,
            var_family,
        ),

        "peso_turno": _build_peso_turno(
            postazioni_stimate=postazioni_stimate,
            count_markings=count_markings,
            count_componenti=len(componenti_unici),
            count_articoli=len(articoli),
        ),

        "tipo_famiglia": _infer_tipo_famiglia(
            articoli,
            family_specs,
        ),

        "classificazione_per_articolo":
        classificazione_per_articolo,

        "dipendenza_parziale":
        dipendenza_parziale,

        "quota_per_complessivo":
        quota_per_complessivo,

        "confidence":
        confidence,

        "discrepancy_flags":
        discrepancy_flags,

    }


def _collect_family_specs_by_drawing(
    specs: pd.DataFrame,
    target: str,
) -> pd.DataFrame:

    normalized_specs = specs["disegno"].astype(str).map(
        normalize_drawing
    )

    return specs[
        normalized_specs == target
    ].copy()


def _estimate_postazioni(
    fasi_uniche: list[str]
) -> list[str]:

    postazioni_stimate: list[str] = []

    for fase in fasi_uniche:

        fase_upper = fase.upper()

        if "GUAINA" in fase_upper:
            postazioni_stimate.append("GUAINE")

        if "PIDMILL" in fase_upper:
            postazioni_stimate.append("PIDMILL")

        if "ZAW-2" in fase_upper:
            postazioni_stimate.append("ZAW-2")

        elif "ZAW-1" in fase_upper:
            postazioni_stimate.append("ZAW-1")

        elif "ZAW" in fase_upper:
            postazioni_stimate.append("ZAW_DA_VERIFICARE")

        if "HENN" in fase_upper:
            postazioni_stimate.append("HENN")

        if "CP" in fase_upper:
            postazioni_stimate.append("CP")

    return sorted(
        set(postazioni_stimate)
    )


def _infer_criticita_tl(
    *,
    postazioni_stimate: list[str],
    componenti_unici: list[str],
) -> list[str]:

    criticita: list[str] = []

    if "GUAINE" in postazioni_stimate:
        criticita.append("carico_guaina")

    if "PIDMILL" in postazioni_stimate:
        criticita.append("tempo_pidmill")

    if any(
        p.startswith("ZAW")
        for p in postazioni_stimate
    ):
        criticita.append("tempo_zaw")

    if len(componenti_unici) > 4:
        criticita.append("multi_component")

    return criticita


def _infer_rotazione(
    *,
    articoli: list[str],
    componenti_unici: list[str],
    fasi_uniche: list[str],
    count_markings: int,
) -> str:

    fase_tokens = " ".join(
        fasi_uniche
    ).upper()

    fast_lane = not any(

        token in fase_tokens

        for token in (

            "PIDMILL",
            "HENN",
            "ZAW",
            "CP",

        )
    )

    single_linear = (

        len(articoli) == 1
        and len(componenti_unici) <= 2
        and len(fasi_uniche) <= 3
        and count_markings <= 1

    )

    return (
        "alta"
        if single_linear and fast_lane
        else "da_verificare"
    )


def _infer_tipo_famiglia(
    articoli: list[str],
    family_specs: pd.DataFrame,
) -> str:

    unique_articoli = {

        str(value).strip()

        for value in articoli

        if str(value).strip()

    }

    if len(unique_articoli) >= 3:
        return "famiglia_complessivo"

    return "famiglia"


def _infer_tassativo(
    articoli: list[str],
    family_specs: pd.DataFrame,
    var_family: pd.DataFrame,
) -> bool:

    payload_parts: list[str] = []

    payload_parts.extend(str(x).strip() for x in articoli if str(x).strip())

    if not family_specs.empty:
        for col in ("famiglia_processo", "raw_json", "articolo", "disegno"):
            if col in family_specs.columns:
                payload_parts.extend(
                    str(x).strip()
                    for x in family_specs[col].fillna("").tolist()
                    if str(x).strip()
                )

    if not var_family.empty:
        for col in ("nome_variante", "raw_json", "articolo"):
            if col in var_family.columns:
                payload_parts.extend(
                    str(x).strip()
                    for x in var_family[col].fillna("").tolist()
                    if str(x).strip()
                )

    payload = " ".join(payload_parts).upper()

    tassativo_markers = (
        "COMPLESSIVO",
        "PARZIALE COMPLESSIVO",
        "PARZIALE_DI_COMPLESSIVO",
        "PARZIALE DI COMPLESSIVO",
    )

    return any(marker in payload for marker in tassativo_markers)


def _build_peso_turno(
    *,
    postazioni_stimate: list[str],
    count_markings: int,
    count_componenti: int,
    count_articoli: int,
) -> dict[str, Any]:

    totale = 1
    per_postazione: dict[str, int] = {}

    if "PIDMILL" in postazioni_stimate:
        totale += 2
        per_postazione["PIDMILL"] = 2

    if "HENN" in postazioni_stimate:
        totale += 2
        per_postazione["HENN"] = 2

    if count_markings >= 2:
        totale += 2

    livello = (
        "alto"
        if totale >= 5
        else "medio"
        if totale >= 3
        else "basso"
    )

    return {
        "totale": totale,
        "livello": livello,
        "per_postazione": per_postazione,
    }


def _build_confidence_summary(
    *,
    postazioni_stimate: list[str],
    registry_override: bool,
) -> dict[str, str]:

    if registry_override:

        return {

            "postazioni_stimate": "CERTO",

            "source": "TL_REGISTRY",

        }

    if "ZAW_DA_VERIFICARE" in postazioni_stimate:

        return {

            "postazioni_stimate": "DA_VERIFICARE",

            "source": "SMF_INFERENCE",

        }

    return {

        "postazioni_stimate": "INFERITO",

        "source": "SMF_INFERENCE",

    }


def _build_discrepancy_flags(
    *,
    postazioni_stimate: list[str],
    registry_override: bool,
) -> dict[str, bool]:

    return {

        "zaw_role_ambiguous":
        "ZAW_DA_VERIFICARE" in postazioni_stimate,

        "registry_not_applied":
        not registry_override,

    }




def _safe_json_load(raw: Any) -> Any:
    if raw is None:
        return {}
    if isinstance(raw, (dict, list)):
        return raw

    s = str(raw).strip()
    if not s:
        return {}

    try:
        return json.loads(s)
    except Exception:
        return {}


def _collect_nested_component_codes(
    *,
    articoli: list[str],
    family_specs: pd.DataFrame,
    comp_family: pd.DataFrame,
    op_family: pd.DataFrame,
) -> list[str]:

    componenti_unici: list[str] = []

    articoli_set = {
        str(value).strip().upper()
        for value in articoli
        if str(value).strip()
    }

    def _is_base_structure(*, tipo: Any = None, ruolo: Any = None) -> bool:
        tipo_norm = str(tipo or "").strip().lower()
        ruolo_norm = str(ruolo or "").strip().lower()
        return tipo_norm == "base" and ruolo_norm == "corpo assieme"

    def add_component(value: Any) -> None:
        code = str(value).strip().upper()
        if not code or code == "NONE":
            return
        if code in articoli_set:
            return
        if code not in componenti_unici:
            componenti_unici.append(code)

    # 1) componenti diretti da BOM_Components.codice_componente
    if "codice_componente" in comp_family.columns:
        for _, row in comp_family.iterrows():
            if _is_base_structure(
                tipo=row.get("tipo"),
                ruolo=row.get("ruolo"),
            ):
                continue
            add_component(row.get("codice_componente"))

    # 2) componenti da BOM_Specs.raw_json.componenti[].codice
    if "raw_json" in family_specs.columns:
        for raw in family_specs["raw_json"].fillna("").tolist():
            payload = _safe_json_load(raw)
            if not isinstance(payload, dict):
                continue

            for item in payload.get("componenti", []) or []:
                if isinstance(item, dict):
                    if _is_base_structure(
                        tipo=item.get("tipo"),
                        ruolo=item.get("ruolo"),
                    ):
                        continue
                    add_component(item.get("codice"))

    # 3) componenti annidati da BOM_Components.extra.componenti_annidati
    if "extra" in comp_family.columns:
        for raw in comp_family["extra"].fillna("").tolist():
            payload = _safe_json_load(raw)
            if not isinstance(payload, dict):
                continue

            for code in payload.get("componenti_annidati", []) or []:
                add_component(code)

    # 4) materiali riferiti da BOM_Operations.extra.materiale_riferimento
    if "extra" in op_family.columns:
        for raw in op_family["extra"].fillna("").tolist():
            payload = _safe_json_load(raw)
            if not isinstance(payload, dict):
                continue

            for code in payload.get("materiale_riferimento", []) or []:
                add_component(code)

    return componenti_unici

def _build_classificazione_per_articolo(
    *,
    articoli: list[str],
    family_specs: pd.DataFrame,
    var_family: pd.DataFrame,
) -> dict[str, str]:
    classificazione: dict[str, str] = {}
    for articolo in articoli:
        specs_rows = family_specs[family_specs["articolo"].astype(str) == articolo]
        var_rows = var_family[var_family["articolo"].astype(str) == articolo]
        payload_parts = specs_rows.get("raw_json", pd.Series(dtype=str)).astype(str).tolist()
        payload_parts.extend(_rows_to_texts(specs_rows))
        payload_parts.extend(_rows_to_texts(var_rows))
        classificazione[articolo] = _classify_article(" ".join(payload_parts))
    return classificazione

def _rows_to_texts(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    return [" ".join(map(str, row)) for row in df.astype(str).itertuples(index=False, name=None)]

def _classify_article(payload: str) -> str:
    text = payload.upper()
    has_parziale = any(token in text for token in ("PARZIALE", "PARTIAL"))
    has_complessivo = any(token in text for token in ("COMPLESSIVO", "COMPLESSIVI", "ASSIEME", "GRUPPO"))
    if has_parziale and has_complessivo:
        return "parziale_di_complessivo"
    if has_complessivo:
        return "complessivo"
    if has_parziale:
        return "parziale"
    return "singolo"

def _build_dipendenza_parziale(
    *,
    classificazione_per_articolo: dict[str, str],
    quota_per_complessivo: int | None,
) -> dict[str, bool]:
    dipendenza: dict[str, bool] = {}
    for articolo, classificazione in classificazione_per_articolo.items():
        dipendenza[articolo] = (
            quota_per_complessivo is not None
            and quota_per_complessivo > 1
            and classificazione in {"parziale", "parziale_di_complessivo"}
        )
    return dipendenza
