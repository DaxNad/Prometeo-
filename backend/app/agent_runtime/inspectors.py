from __future__ import annotations

from datetime import datetime
from typing import Any


def inspect_event(
    *,
    source: str,
    line_id: str,
    event_type: str,
    severity: str,
    payload: dict[str, Any],
) -> dict[str, Any]:

    inspection: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "line_id": line_id,
        "event_type": event_type,
        "severity": severity,
        "event_domain": payload.get("event_domain", "unknown"),
        "possible_anomaly": False,
        "blocked_order": False,
        "overdue": False,
        "urgent_order": False,
    }

    if inspection["event_domain"] == "order":

        if payload.get("blocked") is True:
            inspection["blocked_order"] = True
            inspection["possible_anomaly"] = True

        if payload.get("overdue") is True:
            inspection["overdue"] = True
            inspection["possible_anomaly"] = True

        priority_raw = payload.get("priority")
        priority = str(priority_raw).strip().upper() if priority_raw is not None else ""

        if priority in {"ALTA", "HIGH", "URGENT", "CRITICAL"}:
            inspection["urgent_order"] = True

    if inspection["event_domain"] == "machine":

        if payload.get("machine_state") == "error":
            inspection["possible_anomaly"] = True

    if inspection["event_domain"] == "legacy_bootstrap":

        inspection["possible_anomaly"] = False

    return inspection
