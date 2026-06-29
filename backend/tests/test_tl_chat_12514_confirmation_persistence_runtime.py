import json

from fastapi.testclient import TestClient

from backend.app.api import tl_chat
from backend.app.main import app


client = TestClient(app)


def _valid_payload() -> dict:
    return {
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


def test_tl_chat_persists_12514_confirmation_as_governed_local_evidence(
    tmp_path,
    monkeypatch,
):
    confirmation_path = tmp_path / "spec_intake_confirmation" / "12514_confirmation.json"
    monkeypatch.setattr(
        tl_chat,
        "CONFIRMATION_12514_PATH",
        confirmation_path,
        raising=False,
    )

    response = client.post("/tl/12514/confirmation", json=_valid_payload())

    assert response.status_code == 200
    assert confirmation_path.exists()

    record = json.loads(confirmation_path.read_text(encoding="utf-8"))

    assert record == {
        "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
        "article": "12514",
        "source_capability": "TL_CHAT_12514_CONFIRMATION_STRUCTURED_INPUT_001",
        "confirmation_status": "TL_CONFIRMED_PREVIEW",
        "confidence": "DA_VERIFICARE",
        "planner_eligible": False,
        "promoted_to_certo": False,
        "requires_persistence_review": True,
        "confirmed_fields": [
            "codice",
            "disegno",
            "rev",
            "operations_preview",
            "components_and_tools_preview",
        ],
        "confirmed_by_role": "TL",
        "notes": "Conferma TL su preview 12514",
        "created_at": record["created_at"],
    }
    assert isinstance(record["created_at"], str)
    assert record["created_at"]


def test_tl_chat_blocks_12514_confirmation_overwrite_without_review(
    tmp_path,
    monkeypatch,
):
    confirmation_path = tmp_path / "spec_intake_confirmation" / "12514_confirmation.json"
    confirmation_path.parent.mkdir(parents=True, exist_ok=True)
    confirmation_path.write_text(
        json.dumps(
            {
                "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
                "article": "12514",
                "existing": True,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        tl_chat,
        "CONFIRMATION_12514_PATH",
        confirmation_path,
        raising=False,
    )

    response = client.post("/tl/12514/confirmation", json=_valid_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "confirmation_record_already_exists"
    assert json.loads(confirmation_path.read_text(encoding="utf-8")) == {
        "schema": "TL_CHAT_12514_CONFIRMATION_RECORD_V1",
        "article": "12514",
        "existing": True,
    }
