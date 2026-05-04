from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_real_ingest_order_preview_requires_route():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-001",
            "codice": "12056",
            "qta": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert "route" in data["error"]


def test_real_ingest_order_preview_builds_smfrow_without_write():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-002",
            "cliente": "TEST",
            "codice": "12056",
            "qta": 10,
            "due_date": "2026-05-10",
            "priority": "ALTA",
            "postazione": "ZAW-1",
            "route": ["ZAW-1", "CP"],
            "note": "preview densificazione dominio reale",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["validated"] is True
    assert data["validation"]["is_valid"] is True
    assert data["validation"]["missing_fields"] == []
    assert data["validation"]["warnings"] == []
    assert data["validation"]["blocking_errors"] == []

    preview = data["smf_row_preview"]
    assert preview["id"] == "REAL-PREVIEW-TEST-002"
    assert preview["codice_articolo"] == "12056"
    assert preview["quantita"] == 10
    assert preview["cliente"] == "TEST"
    assert preview["data_scadenza"] == "2026-05-10"
    assert preview["postazione_principale"] == "ZAW-1"
    assert preview["route"] == ["ZAW-1", "CP"]
    assert preview["stato"] == "DA_VALIDARE"
    assert preview["origine"] == "REAL_INGEST_PREVIEW"

    assert "nessuna scrittura" in data["note"]


def test_real_ingest_order_preview_warns_without_final_cp():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-003",
            "codice": "12056",
            "qta": 10,
            "route": ["ZAW-1"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["validation"]["is_valid"] is True
    assert "route_without_final_CP" in data["validation"]["warnings"]

def test_real_ingest_order_preview_normalizes_station_aliases():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-004",
            "codice": "12056",
            "qta": 10,
            "postazione": "ZAW1",
            "route": ["ZAW1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["smf_row_preview"]["postazione_principale"] == "ZAW-1"
    assert data["smf_row_preview"]["route"] == ["ZAW-1", "CP"]
    assert data["validation"]["blocking_errors"] == []


def test_real_ingest_order_preview_blocks_unknown_route_station():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-005",
            "codice": "12056",
            "qta": 10,
            "route": ["BANCO-FANTASMA", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert data["validation"]["is_valid"] is False
    assert any(
        item.startswith("unknown_route_stations")
        for item in data["validation"]["blocking_errors"]
    )


def test_real_ingest_order_preview_warns_on_postazione_route_mismatch():
    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-006",
            "codice": "12056",
            "qta": 10,
            "postazione": "ZAW-2",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert "postazione_mismatch_route_start" in data["validation"]["warnings"]

