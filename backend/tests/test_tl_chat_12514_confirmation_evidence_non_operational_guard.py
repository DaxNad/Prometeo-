import json

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


client = TestClient(app)


def test_12514_persisted_confirmation_evidence_does_not_authorize_planning_or_production(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    (preview_root / "12514_metadata_preview.json").write_text(
        json.dumps(
            {
                "status": "PREVIEW_ONLY",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "article": {
                    "articolo": "12514",
                    "codice": "7056055000A0",
                    "disegno": "A1675003603",
                    "rev": "6",
                },
            }
        ),
        encoding="utf-8",
    )

    confirmation_path = tmp_path / "spec_intake_confirmation" / "12514_confirmation.json"
    confirmation_path.parent.mkdir(parents=True)
    confirmation_path.write_text(
        json.dumps(
            {
                "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
                "article": "12514",
                "source_capability": "TL_CHAT_12514_CONFIRMATION_STRUCTURED_INPUT_001",
                "confirmation_status": "TL_CONFIRMED_PREVIEW",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "promoted_to_certo": False,
                "requires_persistence_review": True,
                "confirmed_fields": ["codice", "disegno", "rev"],
                "confirmed_by_role": "TL",
                "notes": "Conferma TL persistita come evidenza locale",
                "created_at": "2026-06-29T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(tl_chat_api, "CONFIRMATION_12514_PATH", confirmation_path)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)

    response = client.post(
        "/tl/chat",
        json={
            "question": (
                "Render conferma TL per articolo 12514: "
                "è pronto per pianificazione e produzione?"
            ),
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert data["technical_details_hidden"] is True

    assert "Evidenza TL persistita: presente" in data["answer"]
    assert "TL_CONFIRMED_PREVIEW" in data["answer"]
    assert "planner_eligible=false" in data["answer"]
    assert "promoted_to_certo=false" in data["answer"]
    assert "requires_persistence_review=true" in data["answer"]

    assert "non autorizza pianificazione" in data["risk"]
    assert "non produce effetti operativi" in data["risk"]

    forbidden_answer_fragments = [
        "planner_eligible=true",
        "promoted_to_certo=true",
        "PRODUCTION_READY",
        "PLANNING_READY",
        "SOURCE_OF_TRUTH",
    ]
    for fragment in forbidden_answer_fragments:
        assert fragment not in data["answer"]

    forbidden_risk_fragments = [
        "autorizza la pianificazione",
        "abilita pianificazione",
        "produce effetti operativi automatici",
        "fonte operativa certa",
    ]
    for fragment in forbidden_risk_fragments:
        assert fragment not in data["risk"]
