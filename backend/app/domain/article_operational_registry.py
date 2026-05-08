from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

_CACHE_LOADED = False
_CACHE_DATA: dict[str, Any] = {}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _candidate_paths() -> list[Path]:
    explicit = os.getenv("OPERATIONAL_REGISTRY_PATH", "").strip()
    if explicit:
        return [Path(explicit)]

    candidates: list[Path] = []

    smf_base = os.getenv("SMF_BASE_PATH", "").strip()
    if smf_base:
        candidates.append(Path(smf_base) / "finiture" / "article_operational_registry.json")

    if os.getenv("RAILWAY") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_STATIC_URL"):
        candidates.append(Path("/data/local_smf/finiture/article_operational_registry.json"))

    candidates.append(
        _repo_root() / "data/local_smf/finiture/article_operational_registry.json"
    )

    return candidates


def _normalize_code(value: str) -> str:
    return str(value or "").strip().upper()


def _registry_path() -> Path | None:
    for path in _candidate_paths():
        if path.exists():
            return path

    return None


def _load_cache() -> dict[str, Any]:
    global _CACHE_LOADED, _CACHE_DATA

    if _CACHE_LOADED:
        return _CACHE_DATA

    path = _registry_path()
    if path is None:
        _CACHE_LOADED = True
        _CACHE_DATA = {}
        return _CACHE_DATA

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}

    _CACHE_LOADED = True
    _CACHE_DATA = raw if isinstance(raw, dict) else {}
    return _CACHE_DATA


def reset_article_operational_registry_cache() -> None:
    global _CACHE_LOADED, _CACHE_DATA
    _CACHE_LOADED = False
    _CACHE_DATA = {}


def get_operational_registry_entry(article_code: str) -> dict[str, Any] | None:
    if not isinstance(article_code, str) or not article_code.strip():
        return None

    data = _load_cache()
    articles = data.get("articles")

    if not isinstance(articles, dict):
        return None

    wanted = _normalize_code(article_code)

    for key in (article_code, article_code.strip(), wanted):
        entry = articles.get(key)
        if isinstance(entry, dict):
            out = copy.deepcopy(entry)
            out.setdefault("article", wanted)
            out.setdefault("source_registry", "article_operational_registry")
            return out

    for key, entry in articles.items():
        if isinstance(key, str) and _normalize_code(key) == wanted and isinstance(entry, dict):
            out = copy.deepcopy(entry)
            out.setdefault("article", wanted)
            out.setdefault("source_registry", "article_operational_registry")
            return out

    return None
