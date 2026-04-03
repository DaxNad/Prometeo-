from __future__ import annotations

from datetime import date
from typing import Any

from .base import BaseTool


class EventInspectorTool(BaseTool):
    name = "event_inspector"
    description = "Ispeziona payload evento e produce segnali industriali minimi."

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "order_id" in payload or "postazione" in payload or "semaforo" in payload:
            return self._inspect_order_payload(payload)

        return self._inspect_machine_payload(payload)

    def _inspect_machine_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        cycle_time = payload.get("cycle_time", 0)
        machine_state = payload.get("machine_state", "unknown")
        temperature = payload.get("temperature", 0)
        blocked = payload.get("blocked", False)

        possible_anomaly = (
            blocked is True
            or cycle_time > 90
            or temperature > 75
            or machine_state in {"alarm", "fault", "stopped"}
        )

        return {
            "event_domain": "machine",
            "cycle_time": cycle_time,
            "machine_state": machine_state,
            "temperature": temperature,
            "blocked": blocked,
            "possible_anomaly": possible_anomaly,
        }

    def _inspect_order_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        order_id = str(payload.get("order_id", "") or "")
        postazione = str(payload.get("postazione", "") or "")
        stato = str(payload.get("stato", "") or "").strip().lower()
        semaforo = str(payload.get("semaforo", "") or "").strip().upper()
        due_date_raw = str(payload.get("due_date", "") or "").strip()
        note = str(payload.get("note", "") or "")

        try:
            progress = float(payload.get("progress", 0) or 0)
        except (TypeError, ValueError):
            progress = 0.0

        due_in_days = None
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

        possible_anomaly = any(
            [
                blocked_order,
                overdue,
                inconsistent_progress,
                stalled_order,
            ]
        )

        return {
            "event_domain": "order",
            "order_id": order_id,
            "postazione": postazione,
            "stato": stato,
            "semaforo": semaforo,
            "progress": progress,
            "due_date": due_date_raw,
            "due_in_days": due_in_days,
            "overdue": overdue,
            "blocked_order": blocked_order,
            "urgent_order": urgent_order,
            "stalled_order": stalled_order,
            "inconsistent_progress": inconsistent_progress,
            "no_due_date": no_due_date,
            "note_present": bool(note.strip()),
            "possible_anomaly": possible_anomaly,
        }
