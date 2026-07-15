from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


ARTICLE = "99881"


def _request(question: str):
    return TestClient(app).post(
        "/tl/chat",
        json={"question": question, "context": {"article": ARTICLE}},
    )


def test_generic_article_request_keeps_existing_inferred_fallback(monkeypatch):
    fallback_calls: list[str] = []

    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)

    def inferred_summary(article: str):
        fallback_calls.append(article)
        return tl_chat_api.TLChatResponse(
            ok=True,
            answer=f"Profilo inferito per {article}.",
            confidence="INFERITO",
            requires_confirmation=True,
        )

    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", inferred_summary)

    response = _request("Dimmi cosa sai di questo articolo")

    assert response.status_code == 200
    payload = response.json()
    assert fallback_calls == [ARTICLE]
    assert payload["confidence"] == "INFERITO"
    assert "Profilo inferito" in payload["answer"]


def test_explicit_spec_read_uses_real_spec_metadata_as_primary_source(monkeypatch):
    fallback_calls: list[str] = []
    metadata = {
        "article": ARTICLE,
        "confidence": "CERTO",
        "route_status": "CERTO",
        "operational_class": "STANDARD",
        "planner_eligible": False,
        "drawing": "SYNTH-DRAWING-001",
        "rev": "A",
        "route_steps": [],
        "constraints": {},
    }

    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(
        tl_chat_api,
        "_load_local_specs_metadata",
        lambda article: metadata if article == ARTICLE else None,
    )
    monkeypatch.setattr(tl_chat_api, "_load_spec_intake_preview", lambda _article: None)

    def inferred_summary(article: str):
        fallback_calls.append(article)
        raise AssertionError("explicit specification read must not use inferred summary")

    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", inferred_summary)

    response = _request("Leggimi la specifica")

    assert response.status_code == 200
    payload = response.json()
    assert fallback_calls == []
    assert payload["source"] == "local_specs_metadata"
    assert payload["source_status"] == "SOURCE_FOUND"
    assert payload["semantic_status"] == "CERTO"
    assert "SYNTH-DRAWING-001" in payload["answer"]
    assert "Profilo inferito" not in payload["answer"]


def test_explicit_spec_read_reports_missing_without_inferred_fallback(monkeypatch):
    fallback_calls: list[str] = []

    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)

    def inferred_summary(article: str):
        fallback_calls.append(article)
        return tl_chat_api.TLChatResponse(
            ok=True,
            answer=f"Profilo inferito per {article}.",
            confidence="INFERITO",
            requires_confirmation=True,
        )

    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", inferred_summary)

    response = _request("Leggimi la specifica")

    assert response.status_code == 200
    payload = response.json()
    assert fallback_calls == []
    assert payload["source"] == "local_specs_metadata"
    assert payload["source_status"] == "SOURCE_MISSING"
    assert payload["semantic_status"] == "MANCANTE"
    assert payload["confidence"] == "DA_VERIFICARE"
    assert payload["requires_confirmation"] is True
    assert payload["missing_data"] == ["specifica reale articolo"]
    assert "specifica reale" in payload["answer"].lower()
    assert "Profilo inferito" not in payload["answer"]
