from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.sequence_planner import sequence_planner_service
from app.api_production import _build_machine_load
from app.db.session import SessionLocal
import json
from pathlib import Path


def _load_keys(fname: str) -> list[str]:
    p = Path("backend/tests/snapshots") / fname
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)["expected_item_keys"]


def test_snapshot_shapes_and_event_impact_for_zaw1(monkeypatch):
    """
    Mini-regressione: verifica che con un OPEN event su ZAW-1
    - machine-load esponga le chiavi attese e open_events_total >= 1
    - sequence esponga le chiavi attese e event_impact == True
    """
    db: Session = SessionLocal()
    try:
        # Monkeypatch board per non dipendere da viste SQL esterne
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

        # Ensure tabella events e inserisci un evento OPEN su ZAW-1
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
                VALUES ('E-SNAPSHOT-1', 'Seed pressure', 'ZAW-1', 'OPEN', '2026-04-13T10:01:00')
                """
            )
        )
        db.commit()

        # Machine-load
        ml = _build_machine_load(db)
        ml_keys = _load_keys("machine_load_expected_keys.json")
        ml_items = ml.get("items", [])
        zaw = [i for i in ml_items if i.get("station") == "ZAW-1"]
        assert zaw, "nessun item machine-load per ZAW-1"
        for k in ml_keys:
            assert k in zaw[0], f"chiave missing in machine-load: {k}"
        assert zaw[0].get("open_events_total", 0) >= 1

        # Sequence
        seq = sequence_planner_service.build_global_sequence(db)
        seq_keys = _load_keys("sequence_expected_keys.json")
        seq_items = seq.get("items", [])
        zaw_seq = [i for i in seq_items if i.get("critical_station") == "ZAW-1"]
        assert zaw_seq, "nessun item sequence per ZAW-1"
        for k in seq_keys:
            assert k in zaw_seq[0], f"chiave missing in sequence: {k}"
        assert zaw_seq[0].get("event_impact") is True
    finally:
        db.close()
