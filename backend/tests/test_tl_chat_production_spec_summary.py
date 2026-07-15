import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _ask(question: str, article: str | None = None) -> dict:
    payload = {"question": question, "context": {}}
    if article:
        payload["context"]["article"] = article
    response = client.post("/tl/chat", json=payload)
    assert response.status_code == 200
    return response.json()


def test_production_spec_summary_blocks_inferred_fallback_when_source_missing():
    data = _ask("fammi la sintesi produzione", article="999999")
    answer = data["answer"]

    assert "SINTESI PRODUZIONE NON DISPONIBILE" in answer
    assert "Non genero una sintesi produzione da dati inferiti" in answer
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["source_status"] == "SOURCE_MISSING"
    assert data["semantic_status"] == "MANCANTE"


def test_production_spec_summary_detects_explicit_intent_without_generic_fallback():
    data = _ask("scheda produzione", article="999999")
    answer = data["answer"]

    assert "SINTESI PRODUZIONE NON DISPONIBILE" in answer
    assert "INFERITO" not in answer.splitlines()[0]


@pytest.mark.parametrize(
    "question",
    [
        "sintesi produzione del 12514",
        "sintesi produttiva del 12514",
        "scheda operativa del 12514",
    ],
)
def test_production_spec_summary_from_preview_when_available(monkeypatch, question):
    from app.api import tl_chat as tl_chat_api

    preview = {
        "status": "PREVIEW_ONLY",
        "confidence": "PREVIEW_ONLY",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "article": {
            "articolo": "12514",
            "codice": "7056055000A0",
            "disegno": "A1675003603",
            "rev": "6",
        },
        "components_and_tools_preview": [
            {"code": "468922", "description": "guaina"},
            {"code": "468728", "description": "component"},
        ],
        "operations_preview": [
            "LAVAGGIO",
            "ASSEMBLAGGIO",
            "MACCHINA CRIMP RING ZAW",
            "COLLAUDO A PRESSIONE",
        ],
    }

    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)
    monkeypatch.setattr(
        tl_chat_api,
        "_load_spec_intake_preview",
        lambda article: preview if article == "12514" else None,
    )

    data = _ask(question)
    answer = data["answer"]

    assert "12514" in answer
    assert "SINTESI PRODUZIONE" in answer
    assert "Fonte: spec_intake_preview" in answer
    assert "Stato: PREVIEW_ONLY" in answer
    assert "Componenti principali:" in answer
    assert "468922" in answer
    assert "Ciclo operativo:" in answer
    assert "ASSEMBLAGGIO" in answer
