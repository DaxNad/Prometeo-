"""
Test TASK B: compact=true su GET /production/explain.
- verifica che il payload compatto contenga solo i campi previsti
- verifica che il payload default (non compact) contenga i campi aggiuntivi
- non modifica la logica del planner
"""
import os

import pytest

os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
os.environ.setdefault("DATABASE_URL", "")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.main import app  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.sequence_planner import sequence_planner_service  # noqa: E402

COMPACT_FIELDS = {"article", "critical_station", "event_impact", "priority_reason", "risk_level", "signals"}

_FAKE_ROW = {
    "priorita_operativa": 1,
    "articolo": "ART-COMPACT-1",
    "componenti_condivisi": "",
    "quantita": 3,
    "data_spedizione": None,
    "priorita_cliente": "ALTA",
    "complessivo_articolo": "GRP-COMPACT",
    "postazione_critica": "ZAW-1",
    "azione_tl": "PREPARARE_CAMBIO_SERIE",
    "origine_logica": "test",
}


def _ensure_events_table(db: Session) -> None:
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


def test_explain_compact_fields_only(monkeypatch):
    """compact=true: ogni item contiene esattamente i campi del set compatto."""
    db: Session = SessionLocal()
    try:
        _ensure_events_table(db)

        def fake_fetch(_db, view_name):
            return [dict(_FAKE_ROW)]

        monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch)

        client = TestClient(app)
        r = client.get("/production/explain?compact=true")
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        items = data.get("items", [])
        assert items, "Nessun item restituito"
        for item in items:
            assert set(item.keys()) == COMPACT_FIELDS, (
                f"Campi non attesi in compact: {set(item.keys()) - COMPACT_FIELDS}"
            )
    finally:
        db.close()


def test_explain_default_not_compact(monkeypatch):
    """Default (compact assente): ogni item contiene i campi aggiuntivi del planner."""
    db: Session = SessionLocal()
    try:
        _ensure_events_table(db)

        def fake_fetch(_db, view_name):
            return [dict(_FAKE_ROW)]

        monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch)

        client = TestClient(app)
        r = client.get("/production/explain")
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        items = data.get("items", [])
        assert items, "Nessun item restituito"
        # Il payload default deve contenere campi non presenti in compact
        extra_fields = {"article", "quantity", "due_date", "tl_action"}
        for item in items:
            for field in extra_fields:
                assert field in item, f"Campo '{field}' mancante nel payload default"
    finally:
        db.close()


def test_explain_compact_false_equals_default(monkeypatch):
    """compact=false deve essere identico alla chiamata senza parametro."""
    db: Session = SessionLocal()
    try:
        _ensure_events_table(db)

        def fake_fetch(_db, view_name):
            return [dict(_FAKE_ROW)]

        monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch)

        client = TestClient(app)
        r_default = client.get("/production/explain")
        r_false = client.get("/production/explain?compact=false")
        assert r_default.status_code == 200
        assert r_false.status_code == 200
        # Le chiavi degli item devono essere identiche
        keys_default = set(r_default.json()["items"][0].keys()) if r_default.json()["items"] else set()
        keys_false = set(r_false.json()["items"][0].keys()) if r_false.json()["items"] else set()
        assert keys_default == keys_false
    finally:
        db.close()
