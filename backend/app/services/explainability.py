from __future__ import annotations
from typing import Any, Dict


def build_tl_explanation(sequence_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Costruisce un set minimo di motivazioni TL per un item della sequenza.
    Non modifica l'item originale: restituisce un dizionario con
    priority_reason, risk_level, signals.
    """
    open_events = int(sequence_item.get("open_events_total", 0) or 0)
    shared_components = sequence_item.get("shared_components") or []
    cluster_sat = float(sequence_item.get("cluster_saturation", 0) or 0)

    reasons: list[str] = []
    risk = "low"

    if open_events > 0:
        reasons.append("operational event present")
        risk = "high"

    if isinstance(shared_components, list) and len(shared_components) > 0:
        reasons.append("shared component dependency")
        if risk != "high":
            risk = "medium"

    if cluster_sat > 0.5:
        reasons.append("cluster saturation")
        risk = "high"

    priority_reason = "; ".join(reasons) if reasons else "normal flow"

    signals = {
        "events_open": open_events,
        "shared_components_count": len(shared_components) if isinstance(shared_components, list) else 0,
        "cluster_saturation": cluster_sat,
    }

    return {
        "priority_reason": priority_reason,
        "risk_level": risk,
        "signals": signals,
    }

