import os
from fastapi.testclient import TestClient


# Forza backend SQLite per evitare dipendenze da PostgreSQL in test
os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
os.environ.setdefault("DATABASE_URL", "")


from app.main import app  # noqa: E402  (import dopo set env)


def test_smoke_health_and_smf_endpoints():
    client = TestClient(app)

    r_health = client.get("/health")
    assert r_health.status_code == 200
    data = r_health.json()
    assert isinstance(data, dict)
    assert data.get("ok", data.get("status") == "ok") is not False

    r_status = client.get("/smf/status")
    assert r_status.status_code == 200
    status = r_status.json()
    assert "base_path" in status and "exists" in status

    payload = {
        "order_id": "SMOKE-0001",
        "cliente": "SmokeTest",
        "codice": "CODE-SMOKE",
        "qta": 1,
        "postazione": "TEST",
        "source_type": "test",
    }

    r_parse = client.post("/smf/parse-extracted-order", json=payload)
    assert r_parse.status_code == 200
    body = r_parse.json()
    assert body.get("ok") is True
    assert body.get("flow") == "parse_only"
