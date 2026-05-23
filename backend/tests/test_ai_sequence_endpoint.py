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


def test_ai_sequence_endpoint_returns_ok_when_ai_responds(monkeypatch):
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
    class FakeLLMResult:
        response = "RISPOSTA TL MOCK"
        model = "gemma4:e2b"
        fallback_used = False

    def fake_llm(prompt, **kwargs):
        assert kwargs["timeout_seconds"] == 5
        assert kwargs["allow_fallback"] is False
        assert kwargs["model"] == "qwen2.5:1.5b"
        assert kwargs["num_predict"] == 180
        assert kwargs["keep_alive"] == "10m"
        return FakeLLMResult()

    monkeypatch.setattr(ai_module, "run_local_llm_with_metadata", fake_llm)

    client = TestClient(app)
    response = client.post("/ai/sequence", headers={"X-API-Key": "prometeo-local-key"})

    assert response.status_code == 200
    data = response.json()

    assert data["model"] == "gemma4:e2b"
    assert data["configured_model"] == "gemma4:e2b"
    assert data["ai_status"] == "OK"
    assert data["fallback_used"] is False
    assert data["source"] == "sequence_planner"
    assert data["response"] == "RISPOSTA TL MOCK"
    assert data["sequence"]["decision"]["status"] == "ALLOW"
    assert "articolo=12063" in data["prompt_preview"]


def test_ai_sequence_endpoint_returns_partial_when_ai_times_out(monkeypatch):
    from app.api import ai as ai_module

    class FakePlanner:
        def build_global_sequence(self, db):
            return {
                "planner_stage": "TEST_SEQUENCE",
                "items_count": 1,
                "items": [
                    {
                        "article": "12063",
                        "critical_station": "ZAW-1",
                        "customer_priority": "ALTA",
                        "quantity": 80,
                        "tl_action": "AVVIO_IMMEDIATO",
                        "shared_components": ["468728"],
                    }
                ],
            }

    class FakeLLMResult:
        response = "OLLAMA_ERROR: primary=qwen2.5:1.5b: timed out"
        model = "qwen2.5:1.5b"
        fallback_used = False

    monkeypatch.setattr(ai_module, "sequence_planner_service", FakePlanner())
    monkeypatch.setattr(
        ai_module,
        "run_local_llm_with_metadata",
        lambda prompt, **kwargs: FakeLLMResult(),
    )

    client = TestClient(app)
    response = client.post("/ai/sequence", headers={"X-API-Key": "prometeo-local-key"})

    assert response.status_code == 200
    data = response.json()
    assert data["ai_status"] == "PARTIAL"
    assert data["fallback_used"] is True
    assert data["response"] == "AI locale non disponibile entro timeout; planner core valido."
    assert data["warning"] == "AI advisory parziale; usare planner core."
    assert data["sequence"]["planner_stage"] == "TEST_SEQUENCE"
