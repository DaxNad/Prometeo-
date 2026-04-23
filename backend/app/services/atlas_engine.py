def detect_anomaly(event: dict) -> bool:
    if not event:
        return False

    status = str(event.get("status", "")).strip().upper()
    severity = str(event.get("severity", "")).strip().upper()
    event_type = str(event.get("event_type", "")).strip().upper()
    station = str(event.get("station", "")).strip().upper()

    if status != "OPEN":
        return False

    if severity in {"HIGH", "CRITICAL"}:
        return True

    if event_type in {"MATERIAL_SHORTAGE", "MACHINE_STOP"}:
        return True

    if station in {"ZAW-1", "ZAW1", "PIDMILL"} and severity in {"HIGH", "CRITICAL"}:
        return True

    return False
