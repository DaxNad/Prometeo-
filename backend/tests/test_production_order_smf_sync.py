import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _oid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


@pytest.fixture
def client(tmp_path):
    os.environ["SMF_BASE_PATH"] = str(tmp_path)
    return TestClient(app)


def test_create_order_appends_to_smf(client):
    order_id = _oid("TEST-001")

    payload = {
        "order_id": order_id,
        "cliente": "TEST",
        "codice": "12055",
        "qta": 100,
        "postazione": "ZAW1",
        "stato": "da fare",
        "due_date": "2026-04-20",
        "note": "test insert",
    }

    r = client.post("/production/order", json=payload)

    assert r.status_code == 200
    data = r.json()

    assert data["ok"] is True
    assert data["smf_sync"]["ok"] is True
    assert data["smf_sync"]["mode"] == "append_order"


def test_update_order_updates_smf(client):
    order_id = _oid("TEST-002")

    payload = {
        "order_id": order_id,
        "cliente": "TEST",
        "codice": "12055",
        "qta": 50,
        "postazione": "ZAW2",
        "stato": "da fare",
    }

    first = client.post("/production/order", json=payload)
    assert first.status_code == 200

    payload_update = {
        "order_id": order_id,
        "cliente": "TEST",
        "codice": "12055",
        "qta": 80,
        "postazione": "ZAW2",
        "stato": "in corso",
    }

    r = client.post("/production/order", json=payload_update)

    assert r.status_code == 200
    data = r.json()

    assert data["ok"] is True
    assert data["smf_sync"]["ok"] is True
    assert data["smf_sync"]["mode"] == "update_order"


def test_board_state_updated(client):
    order_id = _oid("TEST-003")

    payload = {
        "order_id": order_id,
        "cliente": "TEST",
        "codice": "12055",
        "qta": 20,
        "postazione": "PIDMILL",
    }

    create = client.post("/production/order", json=payload)
    assert create.status_code == 200

    r = client.get("/production/board")

    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True

    ids = [x["order_id"] for x in data["items"]]
    assert order_id in ids


def test_missing_required_fields_rejected(client):
    payload = {
        "order_id": _oid("TEST-004"),
        "cliente": "TEST",
        "codice": "12055",
        "qta": 10,
    }

    r = client.post("/production/order", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "postazione mancante" in data["error"]
