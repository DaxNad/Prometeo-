import json
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List
from uuid import UUID

from backend.app.models.event import Event, EventClose, EventCreate, EventUpdate


class EventService:
    """
    Servizio gestione eventi PROMETEO.
    Versione con persistenza JSON + stato derivato per linea/stazione.
    """

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.events_file = self.data_dir / "events.json"
        self._lock = Lock()

        self._ensure_file(self.events_file, [])
        self.events: Dict[UUID, Event] = {}
        self._load_events()

    # -------------------------
    # FILE HELPERS
    # -------------------------
    def _ensure_file(self, file_path: Path, default_data) -> None:
        if not file_path.exists():
            file_path.write_text(
                json.dumps(default_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def _read_json(self, file_path: Path, default):
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return default

    def _write_json(self, file_path: Path, data) -> None:
        file_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load_events(self) -> None:
        raw = self._read_json(self.events_file, [])
        loaded: Dict[UUID, Event] = {}

        for item in raw:
            event = Event(**item)
            loaded[event.id] = event

        self.events = loaded

    def _save_events(self) -> None:
        ordered = sorted(
            self.events.values(),
            key=lambda e: e.opened_at,
            reverse=False,
        )
        payload = [event.model_dump(mode="json") for event in ordered]
        self._write_json(self.events_file, payload)

    def _sort_events_desc(self, items: List[Event]) -> List[Event]:
        return sorted(items, key=lambda e: e.opened_at, reverse=True)

    def _severity_to_station_status(self, severity: str) -> str:
        mapping = {
            "CRITICAL": "BLOCCATA",
            "HIGH": "ATTENZIONE",
            "MEDIUM": "ATTENZIONE",
            "LOW": "ATTIVA",
        }
        return mapping.get(severity, "ATTIVA")

    # -------------------------
    # CREATE EVENT
    # -------------------------
    def create_event(self, payload: EventCreate) -> Event:
        with self._lock:
            event = Event(**payload.model_dump())
            self.events[event.id] = event
            self._save_events()
            return event

    # -------------------------
    # LIST EVENTS
    # -------------------------
    def list_events(self) -> List[Event]:
        return self._sort_events_desc(list(self.events.values()))

    # -------------------------
    # LIST ACTIVE EVENTS
    # -------------------------
    def list_active_events(self) -> List[Event]:
        items = [e for e in self.events.values() if e.status == "OPEN"]
        return self._sort_events_desc(items)

    # -------------------------
    # GET EVENT
    # -------------------------
    def get_event(self, event_id: UUID) -> Event | None:
        return self.events.get(event_id)

    # -------------------------
    # UPDATE EVENT
    # -------------------------
    def update_event(self, event_id: UUID, payload: EventUpdate) -> Event | None:
        with self._lock:
            event = self.events.get(event_id)
            if not event:
                return None

            data = payload.model_dump(exclude_unset=True)
            updated = event.model_copy(update=data)

            self.events[event_id] = updated
            self._save_events()
            return updated

    # -------------------------
    # CLOSE EVENT
    # -------------------------
    def close_event(self, event_id: UUID, payload: EventClose) -> Event | None:
        with self._lock:
            event = self.events.get(event_id)
            if not event:
                return None

            event.status = "CLOSED"
            event.closed_at = datetime.utcnow()
            event.closed_by = payload.closed_by

            if payload.note:
                event.note = payload.note

            self.events[event_id] = event
            self._save_events()
            return event

    # -------------------------
    # STATE
    # -------------------------
    def get_all_states(self) -> List[dict]:
        """
        Costruisce lo stato corrente di ogni linea/stazione
        a partire dagli eventi attivi (OPEN).
        """
        grouped: Dict[str, List[Event]] = {}

        for event in self.list_active_events():
            key = f"{event.line.strip().upper()}::{event.station.strip().upper()}"
            grouped.setdefault(key, []).append(event)

        states: List[dict] = []

        for _, items in grouped.items():
            latest = max(items, key=lambda e: e.opened_at)
            max_severity_event = max(
                items,
                key=lambda e: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(e.severity),
            )

            states.append(
                {
                    "line": latest.line,
                    "station": latest.station,
                    "state": self._severity_to_station_status(max_severity_event.severity),
                    "active_events": len(items),
                    "last_event_id": str(latest.id),
                    "last_event_title": latest.title,
                    "last_event_type": latest.event_type,
                    "last_severity": latest.severity,
                    "note": latest.note,
                    "updated_at": latest.opened_at,
                }
            )

        states.sort(key=lambda x: x["updated_at"], reverse=True)
        return states

    def get_station_state(self, line: str, station: str) -> dict | None:
        line_norm = line.strip().upper()
        station_norm = station.strip().upper()

        for item in self.get_all_states():
            if (
                item["line"].strip().upper() == line_norm
                and item["station"].strip().upper() == station_norm
            ):
                return item

        return None


event_service = EventService()
