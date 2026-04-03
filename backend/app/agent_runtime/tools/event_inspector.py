from __future__ import annotations

from datetime import date
from typing import Any

from .base import BaseTool


class EventInspectorTool(BaseTool):
    name = "event_inspector"
    description = "Ispeziona payload evento e produce segnali industriali minimi."

    STATION_OVERLOAD_THRESHOLD = 5

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "order_id" in payload or "postazione" in payload or "semaforo" in payload:
            return self._inspect_order_payload(payload)

        return self._inspect_machine_payload(payload)

    def _inspect_machine_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        cycle_time = self._safe_float(payload.get("cycle_time"), default=0.0)
        machine_state = str(payload.get("machine_state", "unknown") or "unknown").strip().lower()
        temperature = self._safe_float(payload.get("temperature"), default=0.0)
        blocked = bool(payload.get("blocked", False))

        anomaly_codes: list[str] = []

        if blocked:
            anomaly_codes.append("MACHINE_BLOCKED")
        if cycle_time > 90:
            anomaly_codes.append("CYCLE_TIME_HIGH")
        if temperature > 75:
            anomaly_codes.append("TEMPERATURE_HIGH")
        if machine_state in {"alarm", "fault", "stopped"}:
            anomaly_codes.append("MACHINE_STATE_ANOMALY")

        possible_anomaly = len(anomaly_codes) > 0

        return {
            "event_domain": "machine",
            "cycle_time": cycle_time,
            "machine_state": machine_state,
            "temperature": temperature,
            "blocked": blocked,
            "anomaly_codes": anomaly_codes,
            "possible_anomaly": possible_anomaly,
        }

    def _inspect_order_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        order_id = str(payload.get("order_id", "") or "").strip()
        postazione = str(payload.get("postazione", "") or "").strip()
        stato = str(payload.get("stato", "") or "").strip().lower().replace("_", " ")
        semaforo = str(payload.get("semaforo", "") or "").strip().upper()
        due_date_raw = str(payload.get("due_date", "") or "").strip()
        note = str(payload.get("note", "") or "")
        priority_raw = str(payload.get("priority", payload.get("priorita", payload.get("priorita_cliente", ""))) or "").strip().upper()
        phase = str(payload.get("phase", payload.get("fase", "")) or "").strip()

        progress = self._safe_float(payload.get("progress"), default=0.0)
        station_load = self._safe_int(
            payload.get("station_load", payload.get("station_queue_pressure", payload.get("queue_size"))),
            default=0,
        )

        due_in_days: int | None = None
        overdue = False

        if due_date_raw:
            try:
                due_date = date.fromisoformat(due_date_raw)
                due_in_days = (due_date - date.today()).days
                overdue = due_in_days < 0
            except ValueError:
                due_in_days = None

        blocked_order = stato == "bloccato" or semaforo == "ROSSO"
        urgent_order = due_in_days is not None and due_in_days <= 1
        stalled_order = stato in {"da fare", "in attesa"} and progress > 0
        inconsistent_progress = stato == "finito" and progress < 100
        no_due_date = due_date_raw == ""

        route_incoherent = not bool(postazione) or not bool(phase)
        priority_mismatch = priority_raw == "ALTA" and stato == "in attesa"
        order_stalled = stalled_order
        station_overload = station_load > self.STATION_OVERLOAD_THRESHOLD

        anomaly_codes: list[str] = []

        if order_stalled:
            anomaly_codes.append("ORDER_STALLED")
        if route_incoherent:
            anomaly_codes.append("ROUTE_INCOHERENT_EVENT")
        if priority_mismatch:
            anomaly_codes.append("PRIORITY_MISMATCH")
        if station_overload:
            anomaly_codes.append("STATION_OVERLOAD")
        if blocked_order:
            anomaly_codes.append("ORDER_BLOCKED")
        if overdue:
            anomaly_codes.append("ORDER_OVERDUE")
        if inconsistent_progress:
            anomaly_codes.append("INCONSISTENT_PROGRESS")

        possible_anomaly = len(anomaly_codes) > 0

        return {
            "event_domain": "order",
            "order_id": order_id,
            "postazione": postazione,
            "phase": phase,
            "stato": stato,
            "priority": priority_raw,
            "semaforo": semaforo,
            "progress": progress,
            "due_date": due_date_raw,
            "due_in_days": due_in_days,
            "overdue": overdue,
            "blocked_order": blocked_order,
            "urgent_order": urgent_order,
            "stalled_order": stalled_order,
            "order_stalled": order_stalled,
            "inconsistent_progress": inconsistent_progress,
            "no_due_date": no_due_date,
            "route_incoherent": route_incoherent,
            "priority_mismatch": priority_mismatch,
            "station_load": station_load,
            "station_overload": station_overload,
            "note_present": bool(note.strip()),
            "anomaly_codes": anomaly_codes,
            "possible_anomaly": possible_anomaly,
        }

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return default
