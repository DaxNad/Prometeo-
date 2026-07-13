from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


ARTICLE = "99877"


def _governed_pack(question: str, article: str | None, limit: int):
    return {
        "mode": "GOVERNED_RETRIEVAL_001",
        "question": question,
        "article": article,
        "evidence": [],
        "constraints": ["read-only", "no planner mutation"],
        "allowed_sources": [
            "local_specs_metadata",
            "spec_intake_preview",
        ],
        "blocked_sources": [],
    }


def _configure_sources(
    monkeypatch,
    *,
    local_rev: str,
    preview_rev: str,
):
    write_calls = []

    local_metadata = {
        "codice": "SYN-99877",
        "drawing": "SYN-DRAWING",
        "rev": local_rev,
        "confidence": "CERTO",
        "route_status": "CERTO",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "planner_admission_status": "ADMITTED",
        "route_steps": [],
        "components": [],
        "constraints": {},
    }

    preview_payload = {
        "status": "PREVIEW_ONLY",
        "confidence": "DA_VERIFICARE",
        "planner_eligible": False,
        "requires_tl_confirmation": True,
        "article": {
            "articolo": ARTICLE,
            "codice": "SYN-99877",
            "disegno": "SYN-DRAWING",
            "rev": preview_rev,
        },
        "operations_preview": [],
        "components_and_tools_preview": [],
    }

    monkeypatch.setattr(
        tl_chat_api,
        "_load_lifecycle_registry",
        lambda: {},
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_load_local_specs_metadata",
        lambda article: local_metadata if article == ARTICLE else None,
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_load_spec_intake_preview",
        lambda article: preview_payload if article == ARTICLE else None,
    )
    monkeypatch.setattr(
        tl_chat_api,
        "build_governed_retrieval_pack",
        _governed_pack,
    )

    def reject_write(*args, **kwargs):
        write_calls.append((args, kwargs))
        raise AssertionError(
            "VERTICAL_SLICE_004 must remain read-only"
        )

    monkeypatch.setattr(
        tl_chat_api,
        "_persist_article_confirmation",
        reject_write,
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_persist_12514_confirmation",
        reject_write,
    )

    return write_calls


def _request():
    return TestClient(app).post(
        "/tl/chat",
        json={
            "question": (
                "Quali dati articolo sono disponibili "
                f"per {ARTICLE}?"
            ),
            "context": {"article": ARTICLE},
        },
    )


def test_tl_chat_multisource_conflict_is_structured_and_read_only(
    monkeypatch,
):
    write_calls = _configure_sources(
        monkeypatch,
        local_rev="A",
        preview_rev="B",
    )

    response = _request()

    assert response.status_code == 200
    payload = response.json()

    assert payload["source"] == "local_specs_metadata"
    assert payload["source_status"] == "SOURCE_AMBIGUOUS"
    assert payload["semantic_status"] == "DA_VERIFICARE"
    assert payload["confidence"] == "DA_VERIFICARE"
    assert payload["requires_confirmation"] is True

    assert payload["conflicts"] == [
        {
            "field_name": "rev",
            "sources": [
                "local_specs_metadata",
                "spec_intake_preview",
            ],
            "values": [
                {
                    "source": "local_specs_metadata",
                    "value": "A",
                },
                {
                    "source": "spec_intake_preview",
                    "value": "B",
                },
            ],
        }
    ]

    assert "Nessun valore è stato riconciliato" in payload["answer"]
    assert payload["missing_data"] == []
    assert write_calls == []

    evidence_sources = {
        item["source_id"]
        for item in payload["evidence_pack"]["evidence"]
    }
    assert f"local_specs_metadata:{ARTICLE}" in evidence_sources
    assert f"spec_intake_preview:{ARTICLE}" in evidence_sources


def test_tl_chat_equal_multisource_values_preserve_existing_behavior(
    monkeypatch,
):
    write_calls = _configure_sources(
        monkeypatch,
        local_rev="A",
        preview_rev="A",
    )

    response = _request()

    assert response.status_code == 200
    payload = response.json()

    assert payload["confidence"] == "CERTO"
    assert payload["requires_confirmation"] is False
    assert "conflicts" not in payload
    assert payload.get("source_status") != "SOURCE_AMBIGUOUS"
    assert write_calls == []
