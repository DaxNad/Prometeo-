from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import tl_chat as tl_chat_api


def test_tl_chat_unknown_article_preserves_safe_missing_behavior(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Dimmi lo stato del codice.",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

    assert "99999" in data["answer"]
    assert "NON DISPONIBILE NEL PROFILO ATTIVO" in data["answer"]

    recommended_action = data["recommended_action"].lower()
    assert "fonte autorizzata" in recommended_action
    assert "profilo" in recommended_action or "specifica" in recommended_action
    assert "conferma del responsabile di produzione" in recommended_action

    answer_and_action = f"{data['answer']} {data['recommended_action']}".lower()
    forbidden_operational_claims = (
        "priorità alta",
        "avvia produzione",
        "metti in produzione",
        "route confermata",
        "componenti confermati",
        "planner_eligible=true",
    )
    for claim in forbidden_operational_claims:
        assert claim not in answer_and_action


def test_tl_chat_unknown_article_exposes_structured_missing_classification(
    monkeypatch,
    tmp_path,
):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Dimmi lo stato del codice.",
            "context": {"article": "99999"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["source"] == "missing"
    assert data["source_status"] == "SOURCE_MISSING"
    assert data["semantic_status"] == "MANCANTE"
    assert data["missing_data"]
    assert any(
        term in " ".join(data["missing_data"]).lower()
        for term in ("profilo", "fonte", "specifica")
    )

    assert data["recommended_action"]
    assert "next_safe_action" not in data


def test_tl_chat_non_missing_response_does_not_expose_missing_classification(
    monkeypatch,
    tmp_path,
):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12514": {
                    "article": "12514",
                    "status": "ATTIVO",
                    "confidence": "CERTO",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)
    response = client.post(
        "/tl/chat",
        json={
            "question": "Dimmi lo stato del codice.",
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "source" not in data
    assert "source_status" not in data
    assert "semantic_status" not in data
    assert "missing_data" not in data
