from fastapi.testclient import TestClient

from app.config import settings
from app.domain import article_profile_resolver as resolver
from app.main import app


def test_protected_endpoint_rejects_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "prometeo_api_key", "contract-key")
    client = TestClient(app)

    payload = {
        "source": "contract_test",
        "line_id": "LINE-1",
        "event_type": "generic",
        "severity": "info",
        "payload": {},
    }

    unauthorized = client.post("/signals/classify", json=payload)
    assert unauthorized.status_code == 401
    assert unauthorized.json().get("detail") == "unauthorized"

    authorized = client.post(
        "/signals/classify",
        json=payload,
        headers={"X-API-Key": "contract-key"},
    )
    assert authorized.status_code != 401


def test_resolver_derived_fallback_is_never_authoritative(monkeypatch, tmp_path):
    monkeypatch.setattr(resolver, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(
        resolver,
        "get_derived_article_profile",
        lambda _article: {"article": "12063", "confidence": "CERTO"},
    )

    profile = resolver.resolve_article_profile("12063")

    assert isinstance(profile, dict)
    assert profile.get("confidence") == "CERTO"
    assert profile.get("authoritative") is False
    assert profile.get("source") == "ARTICLE_PROCESS_MATRIX_DERIVED"
