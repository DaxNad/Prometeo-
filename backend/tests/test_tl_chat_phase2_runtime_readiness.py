from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_tl_chat_phase2_governed_retrieval_runtime_fallback():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Spiegami il retrieval governato e le fonti disponibili.",
            "context": {},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["technical_details_hidden"] is True

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True

    assert "Fonte governata read-only" in data["answer"]
    assert "nessuna scrittura" in data["answer"]
    assert "nessuna decisione automatica" in data["answer"]

    assert data["risk"] == "Risposta basata su retrieval governato preview-only."
    assert "conferma TL richiesta" in data["recommended_action"]

    evidence_pack = data.get("evidence_pack")
    assert isinstance(evidence_pack, dict)
    assert evidence_pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert evidence_pack["question"] == "Spiegami il retrieval governato e le fonti disponibili."
    assert evidence_pack["article"] is None

    assert "read-only" in evidence_pack["constraints"]
    assert "local-only" in evidence_pack["constraints"]
    assert "no LLM calls" in evidence_pack["constraints"]
    assert "no DB writes" in evidence_pack["constraints"]
    assert "no SMF writes" in evidence_pack["constraints"]

    assert "real_smf" in evidence_pack["blocked_sources"]
    assert "database_dumps" in evidence_pack["blocked_sources"]
    assert "secrets" in evidence_pack["blocked_sources"]

    evidence = evidence_pack.get("evidence")
    assert isinstance(evidence, list)
    assert evidence


def test_tl_chat_phase2_evidence_pack_includes_spec_intake_preview_for_article(monkeypatch, tmp_path):
    import json
    from app.api import tl_chat as tl_chat_api
    from app.atlas_engine import governed_retrieval

    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True, exist_ok=True)
    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(
            {
                "status": "PREVIEW_ONLY",
                "runtime_impact": "NONE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "confidence": "DA_VERIFICARE",
                "article": {
                    "articolo": "12514",
                    "codice": "7056055000A0",
                    "disegno": "A1675003603",
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        governed_retrieval,
        "SPEC_INTAKE_PREVIEW_ROOT",
        preview_root,
    )
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_PREVIEW_ROOT",
        preview_root,
    )

    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={
            "question": "Spiegami il retrieval governato e le fonti disponibili per questo articolo.",
            "context": {
                "article": "12514",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["technical_details_hidden"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True

    evidence_pack = data.get("evidence_pack")
    assert isinstance(evidence_pack, dict)
    assert evidence_pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert evidence_pack["article"] == "12514"

    assert "spec_intake_preview" in evidence_pack["allowed_sources"]
    assert "read-only" in evidence_pack["constraints"]
    assert "local-only" in evidence_pack["constraints"]
    assert "no planner mutation" in evidence_pack["constraints"]
    assert "no runtime mutation" in evidence_pack["constraints"]

    evidence = evidence_pack.get("evidence")
    assert isinstance(evidence, list)
    assert any(
        item["source_type"] == "spec_intake_preview"
        and item["source_id"] == "spec_intake_preview:12514"
        and item["confidence"] == "PREVIEW_ONLY"
        and "12514 trovato in spec_intake_preview" in item["text"]
        and "no planner eligibility" in item["text"]
        for item in evidence
    )

    assert data["source"] == "spec_intake_preview"
    assert data["source_status"] == "PREVIEW_ONLY"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert "Conferma TL" in data["missing_data"]
    assert "Abilitazione all'uso per pianificazione" in data["missing_data"]

    assert "Articolo 12514" in data["answer"]
    assert "dati disponibili da fonte preview" in data["answer"]
    assert "planner_eligible=" not in data["answer"]
    assert "can_promote=" not in data["answer"]
    assert "Codice cliente: 7056055000A0" in data["answer"]
    assert "Disegno: A1675003603" in data["answer"]
    assert "Stato: PREVIEW_ONLY" not in data["answer"]
    assert "Affidabilità: DA_VERIFICARE" in data["answer"]
    assert "richiedono conferma TL" in data["answer"]
