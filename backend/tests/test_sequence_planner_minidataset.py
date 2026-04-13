from sqlalchemy import text
from sqlalchemy.orm import Session

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
        db.execute(
            text(
                """
                INSERT OR REPLACE INTO events(id, title, station, status, opened_at)
                VALUES ('E-PLANNER-1', 'Allarme planner', 'ZAW-1', 'OPEN', '2026-04-13T10:01:00')
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
    finally:
        db.close()

