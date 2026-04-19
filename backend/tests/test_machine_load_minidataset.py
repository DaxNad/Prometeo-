from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_production import _build_machine_load
from app.db.session import SessionLocal


def test_machine_load_with_minidataset_and_open_event():
    db: Session = SessionLocal()
    try:
        # board_state minimal schema
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS board_state (
                    id INTEGER PRIMARY KEY,
                    order_id TEXT NOT NULL UNIQUE,
                    cliente TEXT NOT NULL,
                    codice TEXT NOT NULL,
                    qta NUMERIC NOT NULL DEFAULT 0,
                    postazione TEXT NOT NULL,
                    stato TEXT NOT NULL DEFAULT 'da fare',
                    progress NUMERIC NOT NULL DEFAULT 0,
                    semaforo TEXT NOT NULL DEFAULT 'GIALLO',
                    due_date TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT ''
                )
                """
            )
        )
        db.execute(text("DELETE FROM board_state"))

        # Insert minimal rows
        db.execute(
            text(
                """
                INSERT INTO board_state(order_id, cliente, codice, qta, postazione, stato, progress, semaforo, due_date, note, updated_at)
                VALUES
                ('ORD-A', 'ClienteA', 'CODE-A', 5, 'ZAW-1', 'da fare', 0, 'GIALLO', NULL, '', NOW()),
                ('ORD-B', 'ClienteB', 'CODE-B', 3, 'ZAW-2', 'da fare', 0, 'VERDE', NULL, '', NOW())
                """
            )
        )

        # events minimal schema (for SQLite path)
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
                INSERT INTO events(id, title, line, station, event_type, severity, status, opened_at)
                VALUES ('E-1', 'Allarme linea', 'ZAW', 'ZAW-1', 'signal_open', 'HIGH', 'OPEN', '2026-04-13T10:00:00')
                """
            )
        )
        db.commit()

        payload = _build_machine_load(db)
        assert payload.get("planner_stage") == "MACHINE_LOAD_EVENT_AWARE"
        items = payload.get("items", [])
        found = [x for x in items if x.get("station") == 'ZAW-1']
        assert found, "ZAW-1 not aggregated"
        assert found[0].get("open_events_total", 0) >= 1
        assert isinstance(payload.get("warnings", []), list)
    finally:
        db.close()

