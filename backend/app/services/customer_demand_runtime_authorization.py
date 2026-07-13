from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_ID = "customer_demand_registry"
EXPECTED_INDEX_SCHEMA = "PROMETEO_CONTEXT_SOURCE_INDEX_001"
EXPECTED_AUTH_SCHEMA = "PROMETEO_CONTEXT_SOURCE_RUNTIME_AUTHORIZATIONS_001"
REQUIRED_BINDING = "tl_chat_readonly_runtime"
REQUIRED_FIELDS = frozenset(
    {"articolo", "codice_articolo", "quantita", "data_spedizione", "priorita_cliente"}
)
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_INDEX = REPO_ROOT / "memory" / "context_source_index.json"
DEFAULT_RUNTIME_AUTHORIZATIONS = REPO_ROOT / "memory" / "context_source_runtime_authorizations.json"


@dataclass(frozen=True)
class CustomerDemandRuntimeAuthorization:
    authorized: bool
    reason: str
    source_id: str = SOURCE_ID
    structural_origin: str | None = None


def authorize_customer_demand_runtime(
    index_path: Path = DEFAULT_SOURCE_INDEX,
    authorization_path: Path = DEFAULT_RUNTIME_AUTHORIZATIONS,
) -> CustomerDemandRuntimeAuthorization:
    """Deny by default; authorize only when registration and runtime grant agree."""
    index = _read_json(index_path, "SOURCE_INDEX_UNAVAILABLE")
    if isinstance(index, CustomerDemandRuntimeAuthorization):
        return index
    grants = _read_json(authorization_path, "RUNTIME_AUTHORIZATION_UNAVAILABLE")
    if isinstance(grants, CustomerDemandRuntimeAuthorization):
        return grants

    if index.get("schema") != EXPECTED_INDEX_SCHEMA:
        return _deny("SOURCE_INDEX_SCHEMA_INVALID")
    if grants.get("schema") != EXPECTED_AUTH_SCHEMA or grants.get("default_policy") != "deny":
        return _deny("RUNTIME_AUTHORIZATION_SCHEMA_INVALID")

    source = _unique(index.get("sources"), "id", SOURCE_ID)
    if source is None:
        return _deny("SOURCE_REGISTRATION_NOT_UNIQUE")
    grant = _unique(grants.get("authorizations"), "source_id", SOURCE_ID)
    if grant is None:
        return _deny("RUNTIME_AUTHORIZATION_NOT_UNIQUE")

    registration_checks = (
        (source.get("kind") == "database_registry", "SOURCE_KIND_NOT_AUTHORIZED"),
        (source.get("access_mode") == "read_only", "SOURCE_ACCESS_MODE_NOT_READ_ONLY"),
        (source.get("structural_origin") == "customer_demand", "SOURCE_ORIGIN_INVALID"),
        (set(source.get("allowed_fields") or []) == REQUIRED_FIELDS, "SOURCE_FIELDS_NOT_AUTHORIZED"),
    )
    grant_checks = (
        (grant.get("binding") == REQUIRED_BINDING, "SOURCE_BINDING_NOT_AUTHORIZED"),
        (grant.get("enabled") is True, "SOURCE_RUNTIME_DISABLED"),
        (grant.get("access_mode") == "read_only", "RUNTIME_ACCESS_MODE_NOT_READ_ONLY"),
        (grant.get("structural_origin") == source.get("structural_origin"), "RUNTIME_ORIGIN_MISMATCH"),
        (set(grant.get("allowed_fields") or []) == REQUIRED_FIELDS, "RUNTIME_FIELDS_MISMATCH"),
        (grant.get("planner_eligible") is False, "RUNTIME_PLANNER_FORBIDDEN"),
        (grant.get("automatic_promotion") is False, "RUNTIME_PROMOTION_FORBIDDEN"),
        (grant.get("requires_tl_confirmation") is True, "RUNTIME_CONFIRMATION_REQUIRED"),
    )
    for valid, reason in registration_checks + grant_checks:
        if not valid:
            return _deny(reason)

    return CustomerDemandRuntimeAuthorization(
        True,
        "AUTHORIZED_READ_ONLY_TL_CHAT",
        structural_origin="customer_demand",
    )


def _read_json(path: Path, reason: str) -> dict[str, Any] | CustomerDemandRuntimeAuthorization:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return _deny(reason)
    return payload if isinstance(payload, dict) else _deny(reason)


def _unique(items: Any, key: str, value: str) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return None
    matches = [item for item in items if isinstance(item, dict) and item.get(key) == value]
    return matches[0] if len(matches) == 1 else None


def _deny(reason: str) -> CustomerDemandRuntimeAuthorization:
    return CustomerDemandRuntimeAuthorization(False, reason)
