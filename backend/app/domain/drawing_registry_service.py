from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

BASE_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]   # repo root
    / "docs"
    / "domain"
)

REGISTRY_FILE = BASE_PATH / "drawing_behavior_registry.json"


def normalize_drawing(value: object) -> str:
    return str(value or "").strip().replace(" ", "")


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def load_drawing_registry() -> Dict[str, Any]:
    data = _safe_read_json(REGISTRY_FILE)
    return data.get("drawing_behavior", {})


def get_drawing_behavior(drawing: str) -> Optional[Dict[str, Any]]:
    drawing_norm = normalize_drawing(drawing)
    registry = load_drawing_registry()
    node = registry.get(drawing_norm)
    if isinstance(node, dict):
        return node

    for path in sorted(BASE_PATH.glob("registry_entry_*.json")):
        data = _safe_read_json(path)
        if not isinstance(data, dict):
            continue

        if "drawing_behavior" in data:
            behavior_map = data.get("drawing_behavior", {})
            if isinstance(behavior_map, dict):
                entry = behavior_map.get(drawing_norm)
                if isinstance(entry, dict):
                    return entry

        entry = data.get(drawing_norm)
        if isinstance(entry, dict):
            return entry

    return None


def override_postazioni_from_registry(
    *,
    drawing: str,
    inferred_postazioni: list[str]
) -> list[str]:

    behavior = get_drawing_behavior(drawing)

    if not behavior:
        return inferred_postazioni

    registry_stations = behavior.get("stations")

    if not registry_stations:
        return inferred_postazioni

    return sorted(set(registry_stations))
