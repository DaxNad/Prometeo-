from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import tl_chat as tl_chat_api


def test_tl_chat_contract_reads_12402_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "12402": {
                    "status": "DA_VERIFICARE",
                    "source": "riunione_aziendale_memoria_tl",
                    "note": "Codice citato tra quelli da rivalutare.",
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
    assert "riunione_aziendale_memoria_tl" in data["answer"]
    assert "Verifica TL richiesta" in data["recommended_action"]


def test_tl_chat_contract_handles_new_entry_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps({"12410": {"status": "NEW_ENTRY", "source": "tl"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 12410 è nuovo?",
            "context": {"article": "12410"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "INFERITO"
    assert data["requires_confirmation"] is True
    assert "NEW_ENTRY" in data["answer"]
    assert "priorità alta" in data["recommended_action"].lower()


def test_tl_chat_contract_handles_fuori_produzione_from_lifecycle_registry(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps({"12053": {"status": "FUORI_PRODUZIONE", "source": "tl"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Il 12053 è ancora attivo?",
            "context": {"article": "12053"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "INFERITO"
    assert data["requires_confirmation"] is True
    assert "FUORI_PRODUZIONE" in data["answer"]
    assert "Non portare in staging" in data["recommended_action"]


def test_tl_chat_contract_unknown_article_stays_da_verificare(monkeypatch, tmp_path):
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
    assert "non è presente nel lifecycle registry" in data["answer"]
    assert "git" not in data["answer"].lower()
    assert "pytest" not in data["answer"].lower()
    assert "guard" not in data["answer"].lower()


def test_tl_chat_contract_missing_registry_is_safe(monkeypatch, tmp_path):
    missing_dir = tmp_path / "missing"
    missing_registry = missing_dir / "article_lifecycle_registry.json"
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", missing_registry)

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
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert not missing_dir.exists()


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
