from fastapi.testclient import TestClient

from app.main import app
from app.api.ai import _build_sequence_prompt


def test_build_sequence_prompt_contains_real_planner_fields():
    payload = {
        "decision": {
            "status": "ALLOW",
            "priority": 0.8,
            "reasons": ["no_blockers", "zaw_cluster"],
        },
        "items": [
            {
                "article": "12063",
                "critical_station": "ZAW-1",
                "customer_priority": "ALTA",
                "quantity": 80,
                "tl_action": "AVVIO_IMMEDIATO",
                "shared_components": ["468728", "468796"],
                "shared_component_impact_reason": "468796 critical shared across 13 articoli",
            }
        ],
    }

    prompt = _build_sequence_prompt(payload)

    assert "Planner stage:" in prompt
    assert "articolo=12063" in prompt
    assert "postazione=ZAW-1" in prompt
    assert "468796" in prompt


def test_ai_sequence_endpoint_uses_planner_and_llm(monkeypatch):
    from app.api import ai as ai_module

    class FakePlanner:
        def build_global_sequence(self, db):
            return {
                "decision": {
                    "status": "ALLOW",
                    "priority": 0.8,
                    "reasons": ["no_blockers", "zaw_cluster"],
                },
                "items": [
                    {
                        "article": "12063",
                        "critical_station": "ZAW-1",
                        "customer_priority": "ALTA",
                        "quantity": 80,
                        "tl_action": "AVVIO_IMMEDIATO",
                        "shared_components": ["468728", "468796"],
                        "shared_component_impact_reason": "468796 critical shared across 13 articoli",
                    }
                ],
            }

    monkeypatch.setattr(ai_module, "sequence_planner_service", FakePlanner())
    monkeypatch.setattr(ai_module, "run_local_llm", lambda prompt: "RISPOSTA TL MOCK")

    client = TestClient(app)
    response = client.post("/ai/sequence", headers={"X-API-Key": "prometeo-local-key"})

    assert response.status_code == 200
    data = response.json()

    assert data["model"] == "mistral"
    assert data["source"] == "sequence_planner"
    assert data["response"] == "RISPOSTA TL MOCK"
    assert data["sequence"]["decision"]["status"] == "ALLOW"
    assert "articolo=12063" in data["prompt_preview"]
