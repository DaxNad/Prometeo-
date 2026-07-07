from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


def test_public_chat_alias_matches_legacy_tl_chat(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    registry.write_text(
        json.dumps(
            {
                "99997": {
                    "status": "DA_VERIFICARE",
                    "source": "test_source",
                    "note": "Test deterministic lifecycle entry.",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)

    client = TestClient(app)
    payload = {
        "question": "Il 99997 è da verificare?",
        "context": {"article": "99997"},
    }

    legacy_response = client.post("/tl/chat", json=payload)
    public_response = client.post("/chat", json=payload)

    assert legacy_response.status_code == 200
    assert public_response.status_code == 200
    assert public_response.json() == legacy_response.json()
