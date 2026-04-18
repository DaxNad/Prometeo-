from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

BASE_PATH = Path("/Users/davidepiangiolino/Documents/PROMETEO/docs/domain")

REGISTRY_FILE = BASE_PATH / "drawing_behavior_registry.json"


def load_drawing_registry() -> Dict[str, Any]:

    if not REGISTRY_FILE.exists():
        return {}

    try:
        data = json.loads(REGISTRY_FILE.read_text())
    except Exception:
        return {}

    return data.get("drawing_behavior", {})


def get_drawing_behavior(drawing: str) -> Optional[Dict[str, Any]]:

    registry = load_drawing_registry()

    drawing_norm = str(drawing or "").strip().replace(" ", "")

    return registry.get(drawing_norm)


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
