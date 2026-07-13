from __future__ import annotations

import json
from pathlib import Path

from app.services.customer_demand_context_resolver_binding import build_customer_demand_candidate
from app.services.customer_demand_runtime_authorization import (
    CustomerDemandRuntimeAuthorization,
    authorize_customer_demand_runtime,
)


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _index() -> dict:
    return {
        "schema": "PROMETEO_CONTEXT_SOURCE_INDEX_001",
        "sources": [{
            "id": "customer_demand_registry",
            "kind": "database_registry",
            "access_mode": "read_only",
            "runtime_enabled": True,
            "structural_origin": "customer_demand",
            "allowed_fields": [
                "articolo", "codice_articolo", "quantita", "data_spedizione", "priorita_cliente"
            ],
        }],
    }


def _grants(**overrides) -> dict:
    grant = {
        "source_id": "customer_demand_registry",
        "binding": "tl_chat_readonly_runtime",
        "enabled": True,
        "access_mode": "read_only",
        "structural_origin": "customer_demand",
        "allowed_fields": [
            "articolo", "codice_articolo", "quantita", "data_spedizione", "priorita_cliente"
        ],
        "planner_eligible": False,
        "automatic_promotion": False,
        "requires_tl_confirmation": True,
    }
    grant.update(overrides)
    return {
        "schema": "PROMETEO_CONTEXT_SOURCE_RUNTIME_AUTHORIZATIONS_001",
        "default_policy": "deny",
        "authorizations": [grant],
    }


def test_authorization_accepts_only_matching_registration_and_grant(tmp_path):
    result = authorize_customer_demand_runtime(
        _write(tmp_path / "index.json", _index()),
        _write(tmp_path / "grants.json", _grants()),
    )
    assert result == CustomerDemandRuntimeAuthorization(
        True,
        "AUTHORIZED_READ_ONLY_TL_CHAT",
        structural_origin="customer_demand",
    )


def test_authorization_denies_field_drift(tmp_path):
    grants = _grants(allowed_fields=["articolo"])
    result = authorize_customer_demand_runtime(
        _write(tmp_path / "index.json", _index()),
        _write(tmp_path / "grants.json", grants),
    )
    assert result.authorized is False
    assert result.reason == "RUNTIME_FIELDS_MISMATCH"


def test_denied_authorization_never_calls_reader():
    calls = []

    def reader(**kwargs):
        calls.append(kwargs)
        raise AssertionError("reader must not be called")

    candidate = build_customer_demand_candidate(
        articolo="12514",
        reader=reader,
        authorizer=lambda: CustomerDemandRuntimeAuthorization(False, "SOURCE_RUNTIME_DISABLED"),
    )

    assert calls == []
    assert candidate.source_status == "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"
    assert candidate.payload["authorization_reason"] == "SOURCE_RUNTIME_DISABLED"
    assert candidate.payload["missing_data"] == ["customer_demand_runtime_not_authorized"]
    assert candidate.planner_eligible is False
    assert candidate.requires_tl_confirmation is True


def test_authorized_candidate_preserves_canonical_confidence():
    candidate = build_customer_demand_candidate(
        articolo="12514",
        authorizer=lambda: CustomerDemandRuntimeAuthorization(
            True, "AUTHORIZED_READ_ONLY_TL_CHAT", structural_origin="customer_demand"
        ),
        reader=lambda **kwargs: {
            "source_status": "SOURCE_FOUND",
            "confidence": "DA_VERIFICARE",
            "records": [],
            "missing_data": ["record_customer_demand_not_found"],
        },
    )
    assert candidate.source_status == "SOURCE_FOUND"
    assert candidate.confidence == "DA_VERIFICARE"
