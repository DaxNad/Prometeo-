from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import tl_chat as tl_chat_api


def _isolate_tl_chat_sources(monkeypatch, tmp_path):
    monkeypatch.setattr(tl_chat_api, "ROOT", tmp_path)
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", tmp_path / "missing_lifecycle.json")
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", tmp_path / "missing_staging.json")
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", tmp_path / "missing_intake.json")
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", tmp_path / "missing_route_matrix.json")
    monkeypatch.setattr(tl_chat_api, "FAMILY_REGISTRY", tmp_path / "missing_family.json")
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "missing_specs")
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", tmp_path / "missing_spec_preview")


def _write_context_access_binding_source(tmp_path):
    source = tmp_path / "docs" / "tl_context_policy.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "TL Chat runtime fixture. Reader output remains DA_VERIFICARE and non-operational.",
        encoding="utf-8",
    )

    index = tmp_path / "memory" / "context_source_index.json"
    index.parent.mkdir(parents=True)
    index.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "context_access_binding",
                        "path": "docs/tl_context_policy.md",
                        "source_type": "doc_fixture",
                        "access_mode": "read_only",
                        "runtime_enabled": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_tl_chat_runtime_uses_readonly_context_reader_bridge(monkeypatch, tmp_path):
    _isolate_tl_chat_sources(monkeypatch, tmp_path)
    _write_context_access_binding_source(tmp_path)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Quale fonte retrieval governata hai per il 99998?",
            "context": {"article": "99998"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert data["recommended_action"] == (
        "Usare come orientamento; non applicare decisioni operative senza conferma TL."
    )

    answer = data["answer"]
    assert "Answer: Articolo 99998" in answer
    assert "Source: context_access_binding" in answer
    assert "reader_status=READ_OK" in answer
    assert "relative_path=docs/tl_context_policy.md" in answer
    assert "Confidence: DA_VERIFICARE" in answer
    assert "requires_tl_confirmation=true" in answer
    assert "can_promote=false" in answer
    assert "planner_eligible=false" in answer
    assert "Missing data: nessun dato certo promosso; conferma TL richiesta" in answer
    assert "nessuna promozione a CERTO" in answer
    assert "nessuna scrittura" in answer
    assert "nessuna decisione automatica" in answer


def test_tl_chat_runtime_context_reader_missing_source_stays_safe(monkeypatch, tmp_path):
    _isolate_tl_chat_sources(monkeypatch, tmp_path)

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Quale fonte retrieval governata hai per il 99998?",
            "context": {"article": "99998"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True
    assert data["recommended_action"] == "Verificare source_id o fonte ammessa prima di usare il contesto."

    answer = data["answer"]
    assert "Articolo 99998: fonte governata non disponibile" in answer
    assert "Stato fonte: SOURCE_AUTHORIZED_BUT_UNAVAILABLE" in answer
    assert "Non invento contenuto" in answer
    assert "non genero decisioni operative" in answer
    assert "planner_eligible=true" not in answer
    assert "CERTO" not in data["confidence"]
