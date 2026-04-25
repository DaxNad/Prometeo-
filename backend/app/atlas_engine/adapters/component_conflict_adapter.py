
from __future__ import annotations

from app.services.component_usage_service import get_component_conflicts


def evaluate_component_pressure(component_codes: list[str]) -> dict:
    conflicts = get_component_conflicts(component_codes)

    usage_total = sum(len(set(v)) for v in conflicts.values())

    if usage_total >= 20:
        level = "HIGH"
    elif usage_total >= 6:
        level = "MEDIUM"
    elif usage_total > 0:
        level = "LOW"
    else:
        level = "NONE"

    return {
        "score": usage_total,
        "level": level,
        "conflicts": {
            component: sorted(set(articles))
            for component, articles in conflicts.items()
        },
    }
