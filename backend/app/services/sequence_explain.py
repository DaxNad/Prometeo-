from __future__ import annotations
from typing import Any, Dict, List


def explain_global_sequence(seq_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Costruisce spiegazioni leggibili per il TL su come il planner
    ha determinato priorità e segnali di impatto eventi per ogni item.

    Non modifica l'architettura: prende in input il payload già
    costruito da build_global_sequence e restituisce una copia arricchita
    con un campo "explain" per ciascun item.
    """
    if not isinstance(seq_payload, dict):
        return {"ok": False, "error": "invalid_payload"}

    items = list(seq_payload.get("items", []) or [])
    explained: List[Dict[str, Any]] = []

    for it in items:
        # Valori grezzi usati dal planner
        station = it.get("critical_station") or it.get("station")
        open_events = int(it.get("open_events_total", 0) or 0)
        event_impact = bool(it.get("event_impact", False))
        priority = it.get("priority")
        workload = it.get("workload")

        reasons: List[str] = []
        signals: Dict[str, Any] = {}

        if open_events > 0:
            reasons.append(f"Presenza di {open_events} evento/i OPEN su {station}")
            signals["events"] = {"open": open_events, "impact": event_impact}
        else:
            reasons.append("Nessun evento OPEN attivo sulla postazione")
            signals["events"] = {"open": 0, "impact": False}

        if priority is not None:
            reasons.append(f"Priorità planner: {priority}")
            signals["priority"] = priority
        if workload is not None:
            reasons.append(f"Carico stimato: {workload}")
            signals["workload"] = workload

        explained.append({
            **it,
            "explain": {
                "station": station,
                "summary": "; ".join(reasons),
                "signals": signals,
            },
        })

    return {**seq_payload, "items": explained, "explainable": True}

