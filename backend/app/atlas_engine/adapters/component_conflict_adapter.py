from __future__ import annotations

from app.services.component_usage_service import get_component_conflicts


def evaluate_component_pressure(component_codes: list[str]) -> dict:
    conflicts = get_component_conflicts(component_codes)
    details = conflicts.get("details", {}) if isinstance(conflicts, dict) else {}

    usage_total = sum(int(v or 0) for v in details.values())

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
            component: count
            for component, count in sorted(details.items())
        },
    }
