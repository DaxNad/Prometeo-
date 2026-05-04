from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_tl_chat_contract_returns_12402_da_verificare():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 12402 è da verificare?",
            "context": {"article": "12402"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert "12402" in data["answer"]


def test_tl_chat_contract_hides_technical_noise_for_unknown_article():
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
    assert "git" not in data["answer"].lower()
    assert "pytest" not in data["answer"].lower()
    assert "guard" not in data["answer"].lower()


def test_tl_chat_contract_requires_context_for_specific_answer():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Cosa devo verificare?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "codice articolo" in data["recommended_action"].lower()
