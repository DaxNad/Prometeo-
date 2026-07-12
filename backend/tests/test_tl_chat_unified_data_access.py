from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


ARTICLE = "99877"


def _configure_preview_source(monkeypatch, preview_payload):
    write_calls = []

    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)
    monkeypatch.setattr(
        tl_chat_api,
        "_load_spec_intake_preview",
        lambda article: preview_payload if article == ARTICLE else None,
    )
    monkeypatch.setattr(
        tl_chat_api,
        "build_governed_retrieval_pack",
        lambda question, article, limit: {
            "mode": "GOVERNED_RETRIEVAL_001",
            "question": question,
            "article": article,
            "evidence": [
                {
                    "source_id": f"spec_intake_preview:{ARTICLE}",
                    "source_type": "spec_intake_preview",
                    "authority_rank": 12,
                    "confidence": "PREVIEW_ONLY",
                    "text": "Synthetic governed article preview.",
                    "reason": "Retrieved by the existing governed preview source.",
                }
            ],
            "constraints": ["read-only", "no planner mutation"],
            "allowed_sources": ["spec_intake_preview"],
            "blocked_sources": [],
        },
    )

    def reject_write(*args, **kwargs):
        write_calls.append((args, kwargs))
        raise AssertionError("VERTICAL_SLICE_001 must remain read-only")

    monkeypatch.setattr(tl_chat_api, "_persist_article_confirmation", reject_write)
    monkeypatch.setattr(tl_chat_api, "_persist_12514_confirmation", reject_write)

    return write_calls


def test_tl_chat_exposes_article_components_and_operations_with_governed_metadata(
    monkeypatch,
):
    write_calls = _configure_preview_source(
        monkeypatch,
        {
            "status": "PREVIEW_ONLY",
            "confidence": "DA_VERIFICARE",
            "planner_eligible": False,
            "requires_tl_confirmation": True,
            "article": {
                "articolo": ARTICLE,
                "codice": "SYN-99877",
                "disegno": "SYN-DRAWING",
                "rev": "A",
            },
            "operations_preview": ["ASSEMBLAGGIO", "COLLAUDO A PRESSIONE"],
            "components_and_tools_preview": [
                {"code": "SYN-COMP-01", "type": "component"}
            ],
        },
    )
    response = TestClient(app).post(
        "/tl/chat",
        json={
            "question": (
                "Quali dati articolo, componenti e operazioni sono disponibili "
                f"per {ARTICLE}?"
            ),
            "context": {"article": ARTICLE},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert ARTICLE in payload["answer"]
    assert "SYN-99877" in payload["answer"]
    assert "ASSEMBLAGGIO" in payload["answer"]
    assert "COLLAUDO A PRESSIONE VERTICALE" in payload["answer"]
    assert "SYN-COMP-01" in payload["answer"]
    assert payload["source"] == "spec_intake_preview"
    assert payload["source_status"] == "PREVIEW_ONLY"
    assert payload["semantic_status"] == "DA_VERIFICARE"
    assert payload["confidence"] == "DA_VERIFICARE"
    assert payload["confidence"] != "CERTO"
    assert payload["requires_confirmation"] is True
    assert "order_id" not in payload
    assert "shipping_date" not in payload
    assert write_calls == []

    preview_evidence = next(
        item
        for item in payload["evidence_pack"]["evidence"]
        if item["source_id"] == f"spec_intake_preview:{ARTICLE}"
    )
    assert preview_evidence["confidence"] == "PREVIEW_ONLY"
    assert preview_evidence.get("status") == "PREVIEW_ONLY", (
        "Each exposed data block must preserve source, status, and confidence"
    )


def test_tl_chat_declares_missing_components_and_operations_without_inventing_data(
    monkeypatch,
):
    write_calls = _configure_preview_source(
        monkeypatch,
        {
            "status": "PREVIEW_ONLY",
            "confidence": "DA_VERIFICARE",
            "planner_eligible": False,
            "requires_tl_confirmation": True,
            "article": {
                "articolo": ARTICLE,
                "codice": "SYN-99877",
                "disegno": "SYN-DRAWING",
                "rev": "A",
            },
            "operations_preview": [],
            "components_and_tools_preview": [],
        },
    )
    response = TestClient(app).post(
        "/tl/chat",
        json={
            "question": (
                "Quali dati articolo, componenti e operazioni sono disponibili "
                f"per {ARTICLE}?"
            ),
            "context": {"article": ARTICLE},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert ARTICLE in payload["answer"]
    assert "Nessuna operazione disponibile" in payload["answer"]
    assert "Nessun componente disponibile" in payload["answer"]
    assert payload["source_status"] == "PREVIEW_ONLY"
    assert payload["semantic_status"] == "DA_VERIFICARE"
    assert payload["confidence"] != "CERTO"
    assert "order_id" not in payload
    assert "shipping_date" not in payload
    assert write_calls == []
    assert {"operations", "components"} <= set(payload["missing_data"] or []), (
        "Missing component and operation data must be declared structurally"
    )
