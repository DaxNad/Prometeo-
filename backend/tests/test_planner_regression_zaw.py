import os
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

# backend isolato in SQLite per test.
# NON usare setdefault: se DATABASE_URL è esportata, i test sporcano il DB operativo.
os.environ["PROMETEO_DB_BACKEND"] = "sqlite"
os.environ["DATABASE_URL"] = ""

from app.main import app  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.sequence_planner import sequence_planner_service  # noqa: E402


def _seed_orders(client: TestClient) -> None:
    def post(payload: dict):
        r = client.post(
            "/production/order",
            json=payload,
            headers={"X-API-Key": os.getenv("PROMETEO_API_KEY", "test-key")},
        )
        assert r.status_code == 200
        assert r.json().get("ok") is True

    # 3 ordini su ZAW-1 (uno bloccato)
    post({
        "order_id": "TST-ZAW1-001",
        "cliente": "Client",
        "codice": "A",
        "qta": 5,
        "postazione": "ZAW-1",
        "stato": "da fare",
        "priorita": "ALTA"
    })

    post({
        "order_id": "TST-ZAW1-002",
        "cliente": "Client",
        "codice": "B",
        "qta": 3,
        "postazione": "ZAW-1",
        "stato": "da fare",
        "priorita": "MEDIA"
    })

    post({
        "order_id": "TST-ZAW1-003",
        "cliente": "Client",
        "codice": "C",
        "qta": 2,
        "postazione": "ZAW-1",
        "stato": "bloccato",
        "priorita": "ALTA"
    })

    # 1 ordine su ZAW-2
    post({
        "order_id": "TST-ZAW2-001",
        "cliente": "Client",
        "codice": "D",
        "qta": 4,
        "postazione": "ZAW-2",
        "stato": "da fare",
        "priorita": "MEDIA"
    })


def test_planner_regression_zaw(monkeypatch):
    client = TestClient(app)

    db: Session = SessionLocal()
    try:
        db.execute(text("DELETE FROM board_state"))
        db.commit()
    finally:
        db.close()

    db: Session = SessionLocal()
    try:
        db.execute(text("DELETE FROM board_state"))
        db.commit()
    finally:
        db.close()

    # seed ordini
    _seed_orders(client)

    # events: 1 OPEN su ZAW-1
    db: Session = SessionLocal()
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                station TEXT NOT NULL,
                status TEXT NOT NULL,
                opened_at TEXT
            )
        """))
        db.execute(text("DELETE FROM events WHERE id = 'E-REG-ZAW1-1'"))
        db.execute(text("""
            INSERT INTO events(id, line, event_type, severity, title, station, status, opened_at)
            VALUES ('E-REG-ZAW1-1', 'ZAW', 'signal_open', 'HIGH', 'Coda elevata', 'ZAW-1', 'OPEN', '2026-04-13T10:00:00')
        """))
        db.commit()
    finally:
        db.close()

    # machine-load → ZAW-1 deve avere open_events_total > 0
    r_ml = client.get("/production/machine-load", headers={"X-API-Key": os.getenv("PROMETEO_API_KEY", "test-key")})
    assert r_ml.status_code == 200
    items_ml = r_ml.json().get("items", [])
    zaw1 = [i for i in items_ml if i.get("station") == "ZAW-1"]
    assert zaw1 and zaw1[0].get("open_events_total", 0) > 0

    # sequence → per dipendenze dalle viste SQL, monkeypatch del board
    def fake_fetch_station_board(db_sess, view_name: str):
        return [{
            "priorita_operativa": 1,
            "articolo": "CODE-ZAW-A",
            "componenti_condivisi": "COMP-A|COMP-B",
            "quantita": 5,
            "data_spedizione": None,
            "priorita_cliente": "ALTA",
            "complessivo_articolo": "GRP-A",
            "postazione_critica": "ZAW-1",
            "azione_tl": "VERIFICA",
            "origine_logica": view_name,
        }]

    monkeypatch.setattr(
        sequence_planner_service, "fetch_station_board", fake_fetch_station_board
    )

    r_seq = client.get("/production/sequence", headers={"X-API-Key": os.getenv("PROMETEO_API_KEY", "test-key")})
    assert r_seq.status_code == 200
    items_seq = r_seq.json().get("items", [])
    match = [i for i in items_seq if i.get("critical_station") == "ZAW-1"]
    assert match and match[0].get("event_impact") is True

