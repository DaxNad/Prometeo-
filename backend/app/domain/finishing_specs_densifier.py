from __future__ import annotations

import copy
from typing import Any

from app.domain.finishing_specs_index import build_finishing_specs_index


AUTO_NORMALIZABLE = "AUTO_NORMALIZABLE"
ASK_TL = "ASK_TL"
BLOCKED = "BLOCKED"
ALREADY_AUTHORITATIVE = "ALREADY_AUTHORITATIVE"


def _upper_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(v or "").strip().upper() for v in values if str(v or "").strip()]


def _component_codes(metadata: dict[str, Any]) -> list[str]:
    output: list[str] = []

    linked_bom = metadata.get("linked_bom")
    if isinstance(linked_bom, list):
        for item in linked_bom:
            if not isinstance(item, dict):
                continue
            code = str(item.get("component") or "").strip()
            if code:
                output.append(code)

    components = metadata.get("components")
    if isinstance(components, list):
        for code in components:
            value = str(code or "").strip()
            if value:
                output.append(value)

    return list(dict.fromkeys(output))


def _infer_route_steps_from_stations(stations: list[str]) -> list[dict[str, Any]]:
    route: list[str] = []

    def add_once(station: str) -> None:
        if station and station not in route:
            route.append(station)

    for station in stations:
        if station == "LAVAGGIO":
            add_once("LAVAGGIO")
        elif station in {"CONTROLLO_VISIVO", "COLLAUDO_VISIVO", "CONTROLLO_VISIVO_100%"}:
            add_once("CONTROLLO_VISIVO")
        elif station in {"INSERIMENTO_GUAINA", "GUAINA"}:
            add_once("GUAINA")
        elif station == "MARCATURA":
            add_once("MARCATURA")
        elif station == "HENN":
            add_once("HENN")
        elif station == "ZAW1":
            route.append("ZAW1")
        elif station == "ZAW1_2":
            route.append("ZAW1")
        elif station in {"COLLAUDO_PRESSIONE", "CP", "COLLAUDO_VERTICALE"}:
            add_once("CP")
        elif station == "SACCHETTO":
            continue

    return [
        {"seq": idx, "station": station, "status": "CERTO"}
        for idx, station in enumerate(route, start=1)
    ]


def _constraints_from_metadata(
    metadata: dict[str, Any],
    stations: list[str],
    components: list[str],
) -> dict[str, Any]:
    has_henn = "HENN" in stations or "469122" in components or "469124" in components
    has_guaina = "INSERIMENTO_GUAINA" in stations or "GUAINA" in stations or "468922" in components
    zaw1_count = stations.count("ZAW1") + stations.count("ZAW1_2")

    return {
        "has_henn": has_henn,
        "has_guaina": has_guaina,
        "has_zaw1": "ZAW1" in stations or "ZAW1_2" in stations,
        "has_zaw2": False if "ZAW1_2" in stations else ("ZAW2" in stations),
        "primary_zaw_station": "ZAW1" if ("ZAW1" in stations or "ZAW1_2" in stations) else "",
        "zaw_passes": max(1, zaw1_count) if ("ZAW1" in stations or "ZAW1_2" in stations) else 0,
        "do_not_infer_zaw2": "ZAW1_2" in stations,
        "has_pidmill": "PIDMILL" in stations,
        "cp_required": "COLLAUDO_PRESSIONE" in stations or "CP" in stations or "COLLAUDO_VERTICALE" in stations,
        "cp_machine_mode": "VERTICALE_DUE_PIANI" if "COLLAUDO_VERTICALE" in stations else "",
    }


def _support_summary_from_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    stations = _upper_list(metadata.get("stations_expected"))
    components = _component_codes(metadata)

    return {
        "drawing": str(metadata.get("drawing") or metadata.get("disegno") or "").strip(),
        "revision": str(metadata.get("revision") or metadata.get("rev") or "").strip(),
        "stations_expected": stations,
        "components": components,
        "has_henn_hint": "HENN" in stations or "469122" in components or "469124" in components,
        "has_guaina_hint": "INSERIMENTO_GUAINA" in stations or "GUAINA" in stations or "468922" in components,
        "has_zaw1_hint": "ZAW1" in stations or "ZAW1_2" in stations,
        "has_zaw2_hint": "ZAW2" in stations,
        "has_pidmill_hint": "PIDMILL" in stations,
        "has_cp_hint": "COLLAUDO_PRESSIONE" in stations or "CP" in stations or "COLLAUDO_VERTICALE" in stations,
    }


def _suggest_questions(article: Any, support_summary: dict[str, Any]) -> list[str]:
    code = str(article or "").strip()
    stations = support_summary.get("stations_expected") or []
    questions: list[str] = []

    if stations:
        questions.append(
            f"Confermi per {code} la route operativa reale partendo da: {' → '.join(stations)}?"
        )
    else:
        questions.append(f"Confermi la route operativa reale del {code}?")

    if support_summary.get("has_henn_hint"):
        questions.append(f"Confermi che per {code} HENN è presente e va prima di ZAW/innesto rapido?")
    else:
        questions.append(f"Confermi se per {code} HENN è assente?")

    if support_summary.get("has_zaw2_hint"):
        questions.append(f"Per {code}, ZAW2 è postazione reale oppure è un secondo passaggio ZAW1?")
    elif support_summary.get("has_zaw1_hint"):
        questions.append(f"Confermi che per {code} la postazione ZAW corretta è ZAW1?")

    if support_summary.get("has_pidmill_hint"):
        questions.append(f"Confermi che per {code} PIDMILL è realmente presente nella route?")

    if support_summary.get("has_cp_hint"):
        questions.append(f"Confermi che per {code} CP è finale obbligatorio e COLLAUDO_VERTICALE è solo modalità macchina se presente?")

    return questions


def _support_result(
    record: dict[str, Any],
    metadata: dict[str, Any],
    base_reasons: list[str],
) -> dict[str, Any] | None:
    support_summary = _support_summary_from_metadata(metadata)

    has_support = any(
        [
            support_summary.get("drawing"),
            support_summary.get("revision"),
            support_summary.get("stations_expected"),
            support_summary.get("components"),
        ]
    )

    if not has_support:
        return None

    return {
        "article": record.get("article"),
        "classification": ASK_TL,
        "reasons": ["metadata_poor_but_support_available", "tl_confirmation_required"] + base_reasons,
        "support_summary": support_summary,
        "suggested_questions": _suggest_questions(record.get("article"), support_summary),
        "proposed_patch": {},
    }


def _classify_record(record: dict[str, Any], raw_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = list(record.get("issues") or [])

    if record.get("authoritative") is True:
        return {
            "article": record.get("article"),
            "classification": ALREADY_AUTHORITATIVE,
            "reasons": ["metadata_already_authoritative"],
            "support_summary": {},
            "suggested_questions": [],
            "proposed_patch": {},
        }

    metadata = raw_metadata or {}
    stations = _upper_list(metadata.get("stations_expected"))
    components = _component_codes(metadata)

    blockers: list[str] = []
    ask_tl: list[str] = []

    if not metadata:
        blockers.append("metadata_not_readable")

    if not stations:
        blockers.append("missing_stations_expected")

    if record.get("confidence") != "CERTO":
        blockers.append("confidence_not_certo")

    if "ZAW2" in stations:
        ask_tl.append("zaw2_real_station_requires_tl_confirmation")

    if "PIDMILL" in stations:
        ask_tl.append("pidmill_requires_tl_confirmation")

    if "COLLAUDO_VERTICALE" in stations and "COLLAUDO_PRESSIONE" not in stations:
        ask_tl.append("cp_vertical_without_explicit_pressure_check")

    if blockers:
        support = _support_result(record, metadata, blockers + issues)
        if support:
            return support

        return {
            "article": record.get("article"),
            "classification": BLOCKED,
            "reasons": blockers + issues,
            "support_summary": {},
            "suggested_questions": [],
            "proposed_patch": {},
        }

    if ask_tl:
        support_summary = _support_summary_from_metadata(metadata)
        return {
            "article": record.get("article"),
            "classification": ASK_TL,
            "reasons": ask_tl + issues,
            "support_summary": support_summary,
            "suggested_questions": _suggest_questions(record.get("article"), support_summary),
            "proposed_patch": {},
        }

    route_steps = _infer_route_steps_from_stations(stations)
    constraints = _constraints_from_metadata(metadata, stations, components)

    if not route_steps:
        support = _support_result(record, metadata, ["route_steps_not_inferable"] + issues)
        if support:
            return support

        return {
            "article": record.get("article"),
            "classification": BLOCKED,
            "reasons": ["route_steps_not_inferable"] + issues,
            "support_summary": {},
            "suggested_questions": [],
            "proposed_patch": {},
        }

    return {
        "article": record.get("article"),
        "classification": AUTO_NORMALIZABLE,
        "reasons": ["metadata_structured_from_spec", "safe_normalization_rules_available"] + issues,
        "support_summary": _support_summary_from_metadata(metadata),
        "suggested_questions": [],
        "proposed_patch": {
            "schema": "PROMETEO_REAL_DATA_PILOT_V1",
            "route_status": "CERTO",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route_steps": route_steps,
            "constraints": constraints,
            "components": components,
            "normalization_notes": [
                "Preview generata dal Densification Agent.",
                "COLLAUDO_VERTICALE trattato come modalità macchina CP, non fase autonoma.",
                "SACCHETTO trattato come packaging, non fase produttiva primaria.",
                "ZAW1_2, se presente, indica secondo passaggio su ZAW1, non postazione ZAW2.",
                "Fonte autorevole richiesta: specifica di finitura + TL.",
            ],
        },
    }


def build_densification_preview(specs_root=None, metadata_loader=None) -> dict[str, Any]:
    index = build_finishing_specs_index(specs_root)
    records = index.get("records", [])

    results = []
    counts: dict[str, int] = {}

    for record in records:
        raw_metadata = metadata_loader(record) if metadata_loader else None
        result = _classify_record(record, raw_metadata)
        results.append(result)
        classification = str(result.get("classification") or "UNKNOWN")
        counts[classification] = counts.get(classification, 0) + 1

    return {
        "schema": "PROMETEO_FINISHING_SPECS_DENSIFICATION_PREVIEW_V1",
        "mode": "preview_only",
        "records_count": len(results),
        "counts": counts,
        "results": copy.deepcopy(results),
    }
