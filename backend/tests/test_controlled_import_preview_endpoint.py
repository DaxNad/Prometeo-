from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.controlled_import import get_persistent_audit_service, router


class _FakePersistentAuditService:
    def __init__(self) -> None:
        self.calls = []

    def persist_preview_audit(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "ok": True,
            "capability": "CONTROLLED_IMPORT_PERSISTENT_AUDIT_SERVICE_V1",
            "audit_event_id": kwargs.get("audit_event_id") or "AUDIT-ENDPOINT-001",
            "rollback_id": kwargs.get("rollback_id") or "ROLLBACK-ENDPOINT-001",
            "write_mode": "PREVIEW_ONLY",
            "apply_allowed": False,
            "apply_executed": False,
            "persistence_status": "RECORDED",
            "repository_result": {
                "ok": True,
                "persistence_status": "RECORDED",
            },
            "record": {
                "write_mode": "PREVIEW_ONLY",
                "apply_allowed": False,
                "apply_executed": False,
            },
            "error": None,
            "failure_reason": None,
        }


def _client(service=None) -> TestClient:
    app = FastAPI()
    if service is not None:
        app.dependency_overrides[get_persistent_audit_service] = lambda: service
    app.include_router(router)
    return TestClient(app)


def test_controlled_import_preview_endpoint_returns_preview_only_response():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-001",
            "article_code": "ART-ENDPOINT-001",
            "quantity": "4",
            "route": ["ZAW1", "CP"],
            "station": "ZAW1",
            "source_type": "synthetic",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["capability"] == "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1"
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["preview_only"] is True
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "LOW"
    assert data["preview"]["station"] == "ZAW-1"
    assert data["preview"]["route"] == ["ZAW-1", "CP"]
    assert all(value is False for value in data["side_effects"].values())
    assert data["audit_persistence"] == "NONE"
    assert data["apply_allowed"] is False
    assert data["audit_dry_run"]["audit_event_type"] == "CONTROLLED_IMPORT_PREVIEW_EVALUATED"
    assert data["audit_dry_run"]["risk_level"] == "LOW"
    assert data["audit_dry_run"]["write_mode"] == "PREVIEW_ONLY"
    assert data["audit_dry_run"]["human_confirmation_required"] is True
    assert data["audit_dry_run"]["apply_allowed"] is False
    assert all(value is False for value in data["audit_dry_run"]["side_effects"].values())
    assert all(value is False for value in data["audit_dry_run"]["persistence"].values())
    assert data["apply_executed"] is False


def test_controlled_import_preview_endpoint_blocks_incomplete_payload():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={"order_id": "DEMO-ENDPOINT-002", "source_type": "synthetic"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "BLOCKED"
    assert "missing_required_field:article_code" in data["errors"]
    assert "missing_required_field:quantity" in data["errors"]
    assert all(value is False for value in data["side_effects"].values())
    assert data["audit_persistence"] == "NONE"
    assert data["apply_allowed"] is False
    assert data["audit_dry_run"]["preview_ok"] is False
    assert data["audit_dry_run"]["risk_level"] == "BLOCKED"
    assert data["audit_dry_run"]["write_mode"] == "PREVIEW_ONLY"
    assert data["audit_dry_run"]["human_confirmation_required"] is True
    assert data["audit_dry_run"]["apply_allowed"] is False
    assert all(value is False for value in data["audit_dry_run"]["side_effects"].values())
    assert all(value is False for value in data["audit_dry_run"]["persistence"].values())
    assert data["apply_executed"] is False


def test_controlled_import_preview_endpoint_blocks_sensitive_markers():
    client = _client()

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-003",
            "article_code": "ART-ENDPOINT-003",
            "quantity": 1,
            "source_type": "synthetic",
            "note": "data/local_smf/SuperMegaFile_Master.xlsx",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["write_mode"] == "PREVIEW_ONLY"
    assert data["required_human_confirmation"] is True
    assert data["risk_level"] == "BLOCKED"
    assert data["preview"] == {}
    assert "sensitive_input_detected" in data["errors"]
    assert all(value is False for value in data["side_effects"].values())
    assert data["audit_persistence"] == "NONE"
    assert data["apply_allowed"] is False
    assert data["audit_dry_run"]["preview_ok"] is False
    assert data["audit_dry_run"]["risk_level"] == "BLOCKED"
    assert data["audit_dry_run"]["write_mode"] == "PREVIEW_ONLY"
    assert data["audit_dry_run"]["human_confirmation_required"] is True
    assert data["audit_dry_run"]["apply_allowed"] is False
    assert all(value is False for value in data["audit_dry_run"]["side_effects"].values())
    assert all(value is False for value in data["audit_dry_run"]["persistence"].values())


def test_controlled_import_preview_endpoint_default_does_not_persist_audit():
    service = _FakePersistentAuditService()
    client = _client(service=service)

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-004",
            "article_code": "ART-ENDPOINT-004",
            "quantity": 2,
            "route": ["ZAW1"],
            "source_type": "synthetic",
            "actor": "tl-demo",
            "source": "endpoint-test",
            "confirmation_token_hash": "sha256:test-hash",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["audit_persistence"] == "NONE"
    assert "persistent_audit" not in data
    assert data["apply_allowed"] is False
    assert data["apply_executed"] is False
    assert service.calls == []


def test_controlled_import_preview_endpoint_persists_audit_only_when_requested():
    service = _FakePersistentAuditService()
    client = _client(service=service)

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-005",
            "article_code": "ART-ENDPOINT-005",
            "quantity": 3,
            "route": ["ZAW1", "CP"],
            "source_type": "synthetic",
            "persist_audit": True,
            "actor": "tl-demo",
            "source": "endpoint-test",
            "confirmation_token_hash": "sha256:test-hash",
            "audit_event_id": "AUDIT-ENDPOINT-005",
            "rollback_id": "ROLLBACK-ENDPOINT-005",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["audit_persistence"] == "RECORDED"
    assert data["persistent_audit"]["ok"] is True
    assert data["persistent_audit"]["write_mode"] == "PREVIEW_ONLY"
    assert data["persistent_audit"]["apply_allowed"] is False
    assert data["persistent_audit"]["apply_executed"] is False
    assert data["apply_allowed"] is False
    assert data["apply_executed"] is False

    assert len(service.calls) == 1
    call = service.calls[0]
    assert call["actor"] == "tl-demo"
    assert call["source"] == "endpoint-test"
    assert call["confirmation_token_hash"] == "sha256:test-hash"
    assert call["confirmation_token"] is None
    assert call["audit_event_id"] == "AUDIT-ENDPOINT-005"
    assert call["rollback_id"] == "ROLLBACK-ENDPOINT-005"
    assert call["preview_result"]["write_mode"] == "PREVIEW_ONLY"
    assert call["audit_dry_run"]["write_mode"] == "PREVIEW_ONLY"


def test_controlled_import_preview_endpoint_rejects_persistence_without_required_binding_fields():
    service = _FakePersistentAuditService()
    client = _client(service=service)

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-006",
            "article_code": "ART-ENDPOINT-006",
            "quantity": 3,
            "route": ["ZAW1"],
            "source_type": "synthetic",
            "persist_audit": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["audit_persistence"] == "NONE"
    assert data["persistent_audit"]["ok"] is False
    assert data["persistent_audit"]["persistence_status"] == "BLOCKED"
    assert "actor_required" in data["persistent_audit"]["failure_reason"]
    assert "source_required" in data["persistent_audit"]["failure_reason"]
    assert "confirmation_token_hash_required" in data["persistent_audit"]["failure_reason"]
    assert data["persistent_audit"]["apply_allowed"] is False
    assert data["persistent_audit"]["apply_executed"] is False
    assert service.calls == []


def test_controlled_import_preview_endpoint_rejects_clear_confirmation_token_binding():
    service = _FakePersistentAuditService()
    client = _client(service=service)

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-007",
            "article_code": "ART-ENDPOINT-007",
            "quantity": 3,
            "route": ["ZAW1"],
            "source_type": "synthetic",
            "persist_audit": True,
            "actor": "tl-demo",
            "source": "endpoint-test",
            "confirmation_token_hash": "sha256:test-hash",
            "confirmation_token": "CONFERMO IMPORT",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["audit_persistence"] == "NONE"
    assert data["persistent_audit"]["ok"] is False
    assert "clear_confirmation_token_forbidden" in data["persistent_audit"]["failure_reason"]
    assert data["persistent_audit"]["write_mode"] == "PREVIEW_ONLY"
    assert data["persistent_audit"]["apply_allowed"] is False
    assert data["persistent_audit"]["apply_executed"] is False
    assert service.calls == []


def test_controlled_import_preview_endpoint_rejects_persistence_for_blocked_preview():
    service = _FakePersistentAuditService()
    client = _client(service=service)

    response = client.post(
        "/controlled-import/preview",
        json={
            "order_id": "DEMO-ENDPOINT-008",
            "source_type": "synthetic",
            "persist_audit": True,
            "actor": "tl-demo",
            "source": "endpoint-test",
            "confirmation_token_hash": "sha256:test-hash",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "BLOCKED"
    assert data["audit_persistence"] == "NONE"
    assert data["persistent_audit"]["ok"] is False
    assert "blocked_risk_not_persisted_for_preview" in data["persistent_audit"]["failure_reason"]
    assert data["persistent_audit"]["apply_allowed"] is False
    assert data["persistent_audit"]["apply_executed"] is False
    assert service.calls == []
