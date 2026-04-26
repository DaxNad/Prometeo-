from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

_CACHE_LOADED = False
_CACHE_DATA: dict[str, Any] = {}


def _default_smf_base_path() -> Path:
    env_dir = os.getenv("SMF_BASE_PATH", "").strip()
    if env_dir:
        return Path(env_dir)

    if os.getenv("RAILWAY") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_STATIC_URL"):
        return Path("/data/local_smf")

    return Path.home() / "Documents" / "local_smf"


def _matrix_path() -> Path:
    return _default_smf_base_path() / "finiture" / "article_route_matrix.json"


def _normalize_code(value: str) -> str:
    return value.strip().upper()


def _load_cache() -> dict[str, Any]:
    global _CACHE_LOADED, _CACHE_DATA

    if _CACHE_LOADED:
        return _CACHE_DATA

    path = _matrix_path()

    if not path.exists():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    _CACHE_LOADED = True
    _CACHE_DATA = raw if isinstance(raw, dict) else {}
    return _CACHE_DATA


def _extract_profiles(data: dict[str, Any]) -> dict[str, Any]:
    direct = data.get("profiles")
    if isinstance(direct, dict):
        return direct

    articles = data.get("articles")
    if isinstance(articles, dict):
        return articles

    if isinstance(data, dict):
        return data

    return {}


def _find_profile_from_list(data: dict[str, Any], article_code: str) -> dict[str, Any] | None:
    candidates = data.get("profiles")
    if not isinstance(candidates, list):
        candidates = data.get("articles")

    if not isinstance(candidates, list):
        return None

    wanted = _normalize_code(article_code)

    for item in candidates:
        if not isinstance(item, dict):
            continue

        raw_code = (
            item.get("article_code")
            or item.get("codice")
            or item.get("code")
        )

        if isinstance(raw_code, str) and _normalize_code(raw_code) == wanted:
            return item

    return None


def get_article_profile(article_code: str) -> dict[str, Any] | None:
    if not isinstance(article_code, str) or not article_code.strip():
        return None

    data = _load_cache()
    profiles = _extract_profiles(data)
    wanted = _normalize_code(article_code)

    for key in (article_code, article_code.strip(), wanted):
        profile = profiles.get(key)
        if isinstance(profile, dict):
            return copy.deepcopy(profile)

    for key, profile in profiles.items():
        if isinstance(key, str) and _normalize_code(key) == wanted and isinstance(profile, dict):
            return copy.deepcopy(profile)

    list_profile = _find_profile_from_list(data, article_code)

    if isinstance(list_profile, dict):
        return copy.deepcopy(list_profile)

    return None


def _normalize_route(route_value: Any) -> list[str]:
    if isinstance(route_value, list):
        output: list[str] = []

        for item in route_value:
            if isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    output.append(cleaned)

            elif isinstance(item, dict):
                raw = (
                    item.get("station")
                    or item.get("postazione")
                    or item.get("code")
                    or item.get("name")
                )

                if isinstance(raw, str) and raw.strip():
                    output.append(raw.strip())

        return output

    if isinstance(route_value, str):
        cleaned = route_value.strip()
        return [cleaned] if cleaned else []

    return []


def get_article_route(article_code: str) -> list[str]:
    profile = get_article_profile(article_code)

    if not profile:
        return []

    for key in (
        "route",
        "percorso",
        "article_route",
        "stations",
        "postazioni",
    ):
        value = profile.get(key)

        if value:
            normalized = _normalize_route(value)

            if normalized:
                return normalized

    return []


def get_article_signals(article_code: str) -> dict[str, Any]:
    profile = get_article_profile(article_code)

    if not profile:
        return {}

    signals = profile.get("signals")

    if not isinstance(signals, dict):
        signals = profile.get("segnali")

    if isinstance(signals, dict):
        return copy.deepcopy(signals)

    return {}
