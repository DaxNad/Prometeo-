from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.controlled_import import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_controlled_import_preview_endpoint_returns_preview_only_response():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-001",
            "article_code": "ART-ENDPOINT-001",
            "quantity": "4",
            "route": ["ZAW1", "CP"],
            "station": "ZAW1",
            "source_type": "synthetic",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["capability"] == "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1"
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["preview_only"] is True
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "LOW"
    assert data["preview"]["station"] == "ZAW-1"
    assert data["preview"]["route"] == ["ZAW-1", "CP"]
    assert all(value is False for value in data["side_effects"].values())


def test_controlled_import_preview_endpoint_blocks_incomplete_payload():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={"order_id": "DEMO-ENDPOINT-002", "source_type": "synthetic"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "BLOCKED"
    assert "missing_required_field:article_code" in data["errors"]
    assert "missing_required_field:quantity" in data["errors"]
    assert all(value is False for value in data["side_effects"].values())


def test_controlled_import_preview_endpoint_blocks_sensitive_markers():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-003",
            "article_code": "ART-ENDPOINT-003",
            "quantity": 1,
            "source_type": "synthetic",
            "note": "data/local_smf/SuperMegaFile_Master.xlsx",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "BLOCKED"
    assert data["preview"] == {}
    assert "sensitive_input_detected" in data["errors"]
    assert all(value is False for value in data["side_effects"].values())
