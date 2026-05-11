from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from app.domain.article_process_matrix import get_article_profile as get_derived_article_profile

ROOT = Path(__file__).resolve().parents[3]
SPECS_ROOT = ROOT / "specs_finitura"


def _normalize_article(value: Any) -> str:
    return str(value or "").strip().upper()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _load_local_specs_metadata(article_code: str) -> dict[str, Any] | None:
    article = _normalize_article(article_code)
    if not article:
        return None

    metadata_path = SPECS_ROOT / article / "metadata.json"
    if not metadata_path.exists():
        return None

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    if data.get("schema") != "PROMETEO_REAL_DATA_PILOT_V1":
        return None

    if _normalize_article(data.get("article")) != article:
        return None

    return data


def _route_from_metadata(metadata: dict[str, Any]) -> list[str]:
    route_steps = metadata.get("route_steps")
    if not isinstance(route_steps, list):
        return []

    route: list[str] = []
    for step in route_steps:
        if not isinstance(step, dict):
            continue
        station = _clean(step.get("station"))
        if station:
            route.append(station)

    return route


def _signals_from_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    constraints = metadata.get("constraints")
    if not isinstance(constraints, dict):
        constraints = {}

    signals: dict[str, Any] = {
        "source": "LOCAL_SPECS_METADATA",
        "authoritative": True,
    }

    for key in (
        "has_henn",
        "has_guaina",
        "has_pidmill",
        "has_o_ring",
        "has_clip",
        "has_zaw1",
        "has_zaw2",
        "primary_zaw_station",
        "zaw_passes",
        "zaw_double_pass",
        "do_not_infer_zaw2",
        "single_connector_both_ends",
        "cp_required",
        "cp_machine_mode",
        "shared_components",
    ):
        if key in constraints:
            signals[key] = copy.deepcopy(constraints[key])

    return signals


def _profile_from_local_specs_metadata(article_code: str, metadata: dict[str, Any]) -> dict[str, Any]:
    route = _route_from_metadata(metadata)
    confidence = _clean(metadata.get("confidence") or "DA_VERIFICARE").upper()
    route_status = _clean(metadata.get("route_status") or "DA_VERIFICARE").upper()

    return {
        "article": _normalize_article(article_code),
        "source": "LOCAL_SPECS_METADATA",
        "authoritative": True,
        "schema": metadata.get("schema"),
        "confidence": confidence,
        "route_status": route_status,
        "operational_class": _clean(metadata.get("operational_class") or "DA_VERIFICARE").upper(),
        "planner_eligible": bool(metadata.get("planner_eligible")),
        "route": route,
        "signals": _signals_from_metadata(metadata),
        "metadata": copy.deepcopy(metadata),
    }


def resolve_article_profile(article_code: str) -> dict[str, Any] | None:
    """
    Authoritative PROMETEO article profile resolver.

    Source hierarchy:
    1. Local finishing spec metadata generated/confirmed from SPECIFICA DI FINITURA + TL.
    2. Derived article_process_matrix profile only when no authoritative local metadata exists.

    Derived/cache/preview sources must not override local spec/TL metadata.
    """
    local_metadata = _load_local_specs_metadata(article_code)
    if local_metadata:
        return _profile_from_local_specs_metadata(article_code, local_metadata)

    derived = get_derived_article_profile(article_code)
    if isinstance(derived, dict):
        profile = copy.deepcopy(derived)
        profile.setdefault("source", "ARTICLE_PROCESS_MATRIX_DERIVED")
        profile.setdefault("authoritative", False)
        return profile

    return None
