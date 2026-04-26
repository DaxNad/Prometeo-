import os
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


# Forza backend SQLite per evitare dipendenze da PostgreSQL in test
os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
os.environ.setdefault("DATABASE_URL", "")

from app.main import app  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.sequence_planner import sequence_planner_service  # noqa: E402


def test_sequence_explain_endpoint_with_open_event(monkeypatch):
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

        # Assicura tabella events ed inserisce 1 evento OPEN su ZAW-1
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
                VALUES ('E-EXPL-ENDPOINT-1', 'ZAW', 'signal_open', 'HIGH', 'Explain endpoint test', 'ZAW-1', 'OPEN', '2026-04-13T10:05:00')
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
    finally:
        db.close()

    client = TestClient(app)
    r = client.get(
        "/production/sequence/explain",
        headers={"X-API-Key": os.getenv("PROMETEO_API_KEY", "")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert data.get("explainable") is True
    assert data.get("items_count", 0) >= 0
    items = data.get("items", [])
    # L'item per ZAW-1 dovrebbe riflettere l'impatto evento
    match = [i for i in items if i.get("critical_station") == "ZAW-1"]
    if match:
        expl = match[0].get("explain", {})
        ev = (expl.get("signals") or {}).get("events") or {}
        assert ev.get("open", 0) >= 1
