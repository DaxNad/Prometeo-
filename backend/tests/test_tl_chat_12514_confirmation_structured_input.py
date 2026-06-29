from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_tl_chat_accepts_12514_structured_confirmation_input_without_promotion():
    payload = {
        "article": "12514",
        "confirmation_action": "confirm_preview",
        "confirmed_by": "TL",
        "confirmed_fields": [
            "codice",
            "disegno",
            "rev",
            "operations_preview",
            "components_and_tools_preview",
        ],
        "notes": "Conferma TL su preview 12514",
    }

    response = client.post("/tl/12514/confirmation", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["article"] == "12514"
    assert body["confirmation_received"] is True
    assert body["status"] == "TL_CONFIRMED_PREVIEW"
    assert body["confidence"] == "DA_VERIFICARE"
    assert body["planner_eligible"] is False
    assert body["requires_persistence_step"] is True
    assert body["promoted_to_certo"] is False


def test_tl_chat_rejects_structured_confirmation_for_non_12514_article():
    payload = {
        "article": "99999",
        "confirmation_action": "confirm_preview",
        "confirmed_by": "TL",
        "confirmed_fields": ["codice"],
        "notes": "Tentativo fuori scope",
    }

    response = client.post("/tl/12514/confirmation", json=payload)

    assert response.status_code in {400, 422}


def test_tl_chat_rejects_structured_confirmation_with_planner_request():
    payload = {
        "article": "12514",
        "confirmation_action": "confirm_and_plan",
        "confirmed_by": "TL",
        "confirmed_fields": ["codice"],
        "notes": "Tentativo di abilitare planner",
    }

    response = client.post("/tl/12514/confirmation", json=payload)

    assert response.status_code in {400, 422}
