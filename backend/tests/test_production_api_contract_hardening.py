import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path):
    os.environ["SMF_BASE_PATH"] = str(tmp_path)
    return TestClient(app)


def _order_id() -> str:
    return f"CONTRACT-{uuid4().hex[:8]}"


def test_production_order_contract_keeps_legacy_missing_field_response(client):
    response = client.post(
        "/production/order",
        json={
            "order_id": _order_id(),
            "cliente": "TEST",
            "codice": "12066",
            "qta": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["error"] == "postazione mancante"


def test_production_order_contract_rejects_invalid_numeric_payload(client):
    response = client.post(
        "/production/order",
        json={
            "order_id": _order_id(),
            "cliente": "TEST",
            "codice": "12066",
            "qta": "non-numeric",
            "postazione": "ZAW1",
        },
    )

    assert response.status_code == 422


def test_production_events_contract_declares_audit_store(client):
    order_id = _order_id()

    created = client.post(
        "/production/order",
        json={
            "order_id": order_id,
            "cliente": "TEST",
            "codice": "12066",
            "qta": 5,
            "postazione": "ZAW1",
            "stato": "da fare",
        },
    )

    assert created.status_code == 200
    assert created.json()["ok"] is True

    response = client.get("/production/events")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["event_store"] == "production_events"
    assert data["contract"] == "production_audit_readonly"
    assert any(
        item["order_id"] == order_id and item["event_type"] == "order_upserted"
        for item in data["items"]
    )
