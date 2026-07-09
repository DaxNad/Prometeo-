from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_options_preflight_bypasses_api_key_and_returns_cors_headers(monkeypatch):
    monkeypatch.setattr(settings, "prometeo_api_key", "contract-key")
    client = TestClient(app)

    response = client.options(
        "/tl/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-key",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_post_still_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "prometeo_api_key", "contract-key")
    client = TestClient(app)

    response = client.post(
        "/tl/chat",
        json={"question": "Spiegami il retrieval governato."},
    )

    assert response.status_code == 401
    assert response.json().get("detail") == "unauthorized"
