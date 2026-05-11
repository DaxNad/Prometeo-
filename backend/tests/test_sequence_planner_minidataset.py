from sqlalchemy import text
from sqlalchemy.orm import Session

import app.services.sequence_planner as sequence_planner_module
from app.services.sequence_planner import sequence_planner_service
from app.db.session import SessionLocal


def test_sequence_planner_minidataset_with_open_event(monkeypatch):
    db: Session = SessionLocal()
    try:
        # Monkeypatch fetch_station_board to avoid depending on SQL views
        def fake_fetch_station_board(db_sess, view_name: str):
            # Minimal payload expected by planner
            return [
                {
                    "priorita_operativa": 1,
                    "articolo": "CODE-ZAW-A",
                    "componenti_condivisi": "",
                    "quantita": 5,
                    "data_spedizione": None,
                    "priorita_cliente": "MEDIA",
                    "complessivo_articolo": "GRP-A",
                    "postazione_critica": "ZAW-1",
                    "azione_tl": "VERIFICA",
                    "origine_logica": view_name,
                }
            ]

        monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch_station_board)
        monkeypatch.setattr(sequence_planner_module, "build_component_usage_from_db", lambda _db: {})

        # Ensure 'events' table exists (SQLite path)
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    line TEXT,
                    station TEXT NOT NULL,
                    event_type TEXT,
                    severity TEXT,
                    status TEXT NOT NULL,
                    note TEXT,
                    source TEXT,
                    opened_at TEXT,
                    closed_at TEXT,
                    closed_by TEXT
                )
                """
            )
        )
        db.execute(text("DELETE FROM events"))
        db.execute(
            text(
                """
                INSERT INTO events(id, line, event_type, severity, title, station, status, opened_at)
                VALUES ('E-PLANNER-1', 'ZAW', 'signal_open', 'HIGH', 'Allarme planner', 'ZAW-1', 'OPEN', '2026-04-13T10:01:00')
                ON CONFLICT (id) DO UPDATE SET
                    line = EXCLUDED.line,
                    event_type = EXCLUDED.event_type,
                    severity = EXCLUDED.severity,
                    title = EXCLUDED.title,
                    station = EXCLUDED.station,
                    status = EXCLUDED.status,
                    opened_at = EXCLUDED.opened_at
                """
            )
        )
        db.commit()

        payload = sequence_planner_service.build_global_sequence(db)
        assert payload.get("items_count", 0) >= 1
        items = payload.get("items", [])
        match = [i for i in items if i.get("critical_station") == "ZAW-1"]
        assert match, "planner items for ZAW-1 missing"
        assert any(i.get("event_impact") is True for i in match), "event impact not propagated"

        diagnostic_item = match[0]
        assert "planner_eligible" in diagnostic_item
        assert "planner_admitted" in diagnostic_item
        assert "admission_reasons" in diagnostic_item
        assert "human_override_allowed" in diagnostic_item
        assert "planner_admission_rule" in diagnostic_item

        assert diagnostic_item["human_override_allowed"] is True
        assert diagnostic_item["planner_admitted"] is False
        assert "blocking_constraint_open" in diagnostic_item["admission_reasons"]
    finally:
        db.close()

def test_sequence_planner_marks_ragnetto_group_dependency(monkeypatch):
    db: Session = SessionLocal()
    try:
        def fake_fetch_station_board(db_sess, view_name: str):
            return [
                {
                    "priorita_operativa": 1,
                    "articolo": "12074",
                    "componenti_condivisi": "",
                    "quantita": 5,
                    "data_spedizione": None,
                    "priorita_cliente": "MEDIA",
                    "complessivo_articolo": "12074",
                    "postazione_critica": "ZAW-2",
                    "azione_tl": "AVVIO_IMMEDIATO",
                    "origine_logica": view_name,
                }
            ]

        monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch_station_board)
        monkeypatch.setattr(sequence_planner_module, "build_component_usage_from_db", lambda _db: {})
        monkeypatch.setattr(sequence_planner_module, "_get_open_events_by_station", lambda _db: {})

        payload = sequence_planner_service.build_global_sequence(db)
        items = payload.get("items", [])
        item = [i for i in items if i.get("article") == "12074"][0]

        assert item["article_group_id"] == "ragnetto_12074_12078"
        assert item["group_dependency"] is True
        assert item["group_planner_policy"] == "GROUP_DEPENDENCY_NOT_INDEPENDENT"
        assert item["group_status"] == "DA_MODELLARE"
        assert "group_dependency_not_structured" in item["diagnostic_reasons"]
        assert item["planner_enforcement"] is False

        assert "group_dependency_not_structured" not in item["admission_reasons"]
    finally:
        db.close()

