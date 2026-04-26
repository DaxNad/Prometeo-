from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.sequence_planner import sequence_planner_service
from app.services.sequence_explain import explain_global_sequence


def test_explain_builder_adds_reasons(monkeypatch):
    db: Session = SessionLocal()
    try:
        def fake_fetch_station_board(db_sess, view_name: str):
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

        monkeypatch.setattr(
            sequence_planner_service, "fetch_station_board", fake_fetch_station_board
        )

        # Seed evento OPEN su ZAW-1 (SQLite in-proc)
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
                VALUES ('E-EXPL-1', 'ZAW', 'signal_open', 'HIGH', 'Test Impact', 'ZAW-1', 'OPEN', '2026-04-13T10:01:00')
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

        seq = sequence_planner_service.build_global_sequence(db)
        out = explain_global_sequence(seq)

        assert out.get("explainable") is True
        items = out.get("items", [])
        assert items, "nessun item explainable"
        match = [i for i in items if i.get("critical_station") == "ZAW-1"]
        assert match, "manca item per ZAW-1"
        expl = match[0].get("explain", {})
        assert expl.get("signals", {}).get("events", {}).get("open", 0) >= 1
        assert "evento/i OPEN" in (expl.get("summary") or "")
    finally:
        db.close()
