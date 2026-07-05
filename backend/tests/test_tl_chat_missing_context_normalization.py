from fastapi.testclient import TestClient

from app.main import app


def test_tl_chat_missing_context_exposes_structured_classification():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Dimmi le informazioni operative disponibili"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["source"] == "missing"
    assert data["source_status"] == "SOURCE_MISSING"
    assert data["semantic_status"] == "MANCANTE"
    assert data["missing_data"] == ["codice articolo"]
    assert "next_safe_action" not in data


def test_tl_chat_governed_evidence_without_article_is_not_classified_as_missing():
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Spiegami confidence CERTO INFERITO DA_VERIFICARE"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["evidence_pack"]["article"] is None
    assert "source" not in data
    assert "source_status" not in data
    assert "semantic_status" not in data
    assert "missing_data" not in data
