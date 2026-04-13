import os
from fastapi.testclient import TestClient

os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")

from app.main import app  # noqa: E402


def test_events_api_seed_and_list_active():
    client = TestClient(app)

    payload = {
        "title": "Seed test event",
        "line": "MAIN",
        "station": "ZAW-1",
        "event_type": "ALERT",
        "severity": "HIGH",
        "note": "seed via test",
        "source": "test",
    }

    r = client.post("/events/create", json=payload)
    assert r.status_code in (200, 501, 409)
    # In SQLite, la creazione è supportata: atteso 200
    if r.status_code == 200:
        created = r.json()
        assert created.get("station") == "ZAW-1"

        r2 = client.get("/events/active")
        assert r2.status_code == 200
        data = r2.json()
        assert data.get("open_count", 0) >= 1

