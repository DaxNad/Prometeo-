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
    assert "nessuna promozione a CERTO" in data["answer"]
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
