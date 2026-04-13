import json
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.api_production import _build_machine_load
from app.services.sequence_planner import sequence_planner_service


def _load_keys(fname: str) -> list[str]:
    p = Path("backend/tests/snapshots") / fname
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)["expected_item_keys"]


def test_snapshot_keys_only_for_machine_load_and_sequence(monkeypatch):
    db: Session = SessionLocal()
    try:
        # Garantisce la tabella events (SQLite path); non impone conteggi
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    station TEXT NOT NULL,
                    status TEXT NOT NULL,
                    opened_at TEXT
                )
                """
            )
        )
        db.commit()

        # Machine-load: verifica solo la presenza delle chiavi richieste
        ml = _build_machine_load(db)
        ml_keys = _load_keys("machine_load_expected.json")
        items = ml.get("items", [])
        if items:
            for k in ml_keys:
                assert k in items[0]

        # Sequence: monkeypatch del board per autonomia dai view SQL
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

        seq = sequence_planner_service.build_global_sequence(db)
        seq_keys = _load_keys("sequence_expected.json")
        seq_items = seq.get("items", [])
        if seq_items:
            for k in seq_keys:
                assert k in seq_items[0]
    finally:
        db.close()

