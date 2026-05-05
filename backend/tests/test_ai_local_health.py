from __future__ import annotations

import json
from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.api import ai as ai_api


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def test_ai_local_health_available(monkeypatch):
    def fake_urlopen(url, timeout=2):
        assert url == "http://127.0.0.1:11434/api/tags"
        assert timeout == 2
        return _FakeResponse(
            {
                "models": [
                    {"name": "mistral:latest"},
                    {"name": "llama3.2:3b"},
                ]
            }
        )

    monkeypatch.setattr(ai_api.urllib.request, "urlopen", fake_urlopen)

    client = TestClient(app)
    response = client.get("/ai/local/health")

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["provider"] == "ollama"
    assert data["available"] is True
    assert data["base_url"] == "http://127.0.0.1:11434"
    assert data["models"] == ["mistral:latest", "llama3.2:3b"]
    assert data["writable"] is False
    assert data["decision_authority"] is False
    assert "no production decision authority" in data["note"]


def test_ai_local_health_unavailable(monkeypatch):
    def fake_urlopen(url, timeout=2):
        raise OSError("connection refused")

    monkeypatch.setattr(ai_api.urllib.request, "urlopen", fake_urlopen)

    client = TestClient(app)
    response = client.get("/ai/local/health")

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["provider"] == "ollama"
    assert data["available"] is False
    assert data["models"] == []
    assert data["writable"] is False
    assert data["decision_authority"] is False
    assert "connection refused" in data["error"]
