from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.article_specification_confirmation import router
from app.domain.article_operational_registry import (
    reset_article_operational_registry_cache,
)
from app.main import app as main_app


ARTICLE = "SYNTH-CONFIRM-01"


def _client() -> TestClient:
    api = FastAPI()
    api.include_router(router)
    return TestClient(api)


def _payload(**overrides):
    payload = {
        "article": ARTICLE,
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "tl_confirmation_required": False,
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "audit_note": "Conferma umana esplicita da UI.",
    }
    payload.update(overrides)
    return payload


def test_confirmation_endpoint_persists_governed_human_confirmation(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    registry_path.write_text(
        json.dumps({"version": "synthetic", "articles": {}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    response = _client().post(
        "/article-specification/confirm",
        json=_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "ORCHESTRATED"
    assert data["writer_called"] is True
    assert data["persisted"] is True
    assert data["created"] is True
    assert data["updated"] is False
    assert data["error_code"] is None

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    record = stored["articles"][ARTICLE]
    assert record["operational_class"] == "STANDARD"
    assert record["planner_eligible"] is True
    assert record["tl_confirmation_required"] is False
    assert record["authority_role"] == "RESPONSABILE_PRODUZIONE"
    assert record["confirmation_origin"] == "HUMAN_EXPLICIT_CONFIRMATION"

    reset_article_operational_registry_cache()


def test_confirmation_endpoint_rejects_unauthorized_authority_without_writer():
    response = _client().post(
        "/article-specification/confirm",
        json=_payload(authority_role="OPERATORE"),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["status"] in {"REJECTED", "NOT_EXECUTED"}
    assert data["writer_called"] is False
    assert data["persisted"] is False
    assert data["error_code"] in {
        "UNAUTHORIZED_AUTHORITY_ROLE",
        "AUTHORITY_REQUIRED",
    }


def test_confirmation_endpoint_rejects_missing_required_field():
    response = _client().post(
        "/article-specification/confirm",
        json={
            "article": ARTICLE,
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "tl_confirmation_required": False,
            "authority_role": "RESPONSABILE_PRODUZIONE",
        },
    )

    assert response.status_code == 422


def test_confirmation_endpoint_is_registered_in_main_app(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    registry_path.write_text(
        json.dumps({"version": "synthetic", "articles": {}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    response = TestClient(main_app).post(
        "/article-specification/confirm",
        json=_payload(article="SYNTH-MAIN-01"),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ORCHESTRATED"

    reset_article_operational_registry_cache()


def test_confirmation_endpoint_preserves_write_succeeded_readback_failed(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    registry_path.write_text(
        json.dumps({"version": "synthetic", "articles": {}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    monkeypatch.setattr(
        "app.services.article_operational_confirmation_service."
        "get_operational_registry_entry",
        lambda _article: None,
    )
    reset_article_operational_registry_cache()

    response = _client().post(
        "/article-specification/confirm",
        json=_payload(article="SYNTH-READBACK-FAIL"),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["status"] == "ORCHESTRATION_FAILED"
    assert data["writer_called"] is True
    assert data["persisted"] is True
    assert data["created"] is False
    assert data["updated"] is False
    assert data["error_code"] == "WRITE_SUCCEEDED_READBACK_FAILED"

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    assert "SYNTH-READBACK-FAIL" in stored["articles"]

    reset_article_operational_registry_cache()


def test_confirmation_endpoint_preserves_write_failure_without_persistence(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    original_registry = {"version": "synthetic", "articles": {}}
    registry_path.write_text(
        json.dumps(original_registry),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    monkeypatch.setattr(
        "app.services.article_operational_confirmation_service."
        "_atomic_write_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError("synthetic write failure")
        ),
    )
    reset_article_operational_registry_cache()

    response = _client().post(
        "/article-specification/confirm",
        json=_payload(article="SYNTH-WRITE-FAIL"),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["status"] == "ORCHESTRATION_FAILED"
    assert data["writer_called"] is True
    assert data["persisted"] is False
    assert data["created"] is False
    assert data["updated"] is False
    assert data["error_code"] == "WRITE_FAILED"

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    assert stored == original_registry

    reset_article_operational_registry_cache()
