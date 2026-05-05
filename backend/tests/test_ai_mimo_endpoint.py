from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_mimo_without_env_returns_disabled():
    res = client.post("/ai/mimo", json={"prompt": "test"})
    data = res.json()

    assert res.status_code == 200
    assert data["enabled"] is False


def test_ai_mimo_requires_prompt():
    res = client.post("/ai/mimo", json={})
    data = res.json()

    assert res.status_code == 200
    assert data["enabled"] is False
    assert "prompt mancante" in data["error"]


def test_ai_mimo_validate_sequence_safe_without_env():
    res = client.post("/ai/mimo/validate-sequence", json={
        "sequence": {},
        "events": []
    })

    data = res.json()

    assert res.status_code == 200
    assert data["enabled"] is False or "validation" in data
