from fastapi.testclient import TestClient

from app.api import events as events_api
from app.config import settings
from app.main import app


class _FailingEventsRepo:
    def create_event(self, _payload):
        raise Exception('relation "events" does not exist')


def test_events_create_failure_is_explicit_not_silent(monkeypatch):
    monkeypatch.setattr(settings, "prometeo_api_key", "contract-key")
    monkeypatch.setattr(events_api, "get_events_repository", lambda: _FailingEventsRepo())
    client = TestClient(app)

    payload = {
        "title": "contract-observability",
        "line": "LINE-1",
        "station": "ZAW-1",
        "event_type": "ALERT",
        "severity": "HIGH",
    }

    response = client.post(
        "/events/create",
        json=payload,
        headers={"X-API-Key": "contract-key"},
    )

    assert response.status_code == 409
    detail = response.json().get("detail", "")
    assert "/production/order" in detail
    assert "non allineato" in detail.lower()


def test_events_anomaly_without_data_returns_explicit_status(monkeypatch):
    monkeypatch.setattr(settings, "prometeo_api_key", "contract-key")

    class _EmptyRepo:
        def list_events(self):
            return []

    monkeypatch.setattr(events_api, "get_events_repository", lambda: _EmptyRepo())
    client = TestClient(app)

    response = client.get("/events/anomaly", headers={"X-API-Key": "contract-key"})
    assert response.status_code == 200
    assert response.json() == {"status": "no_data"}
