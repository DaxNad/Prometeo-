from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_ID = "customer_demand_registry"
EXPECTED_SCHEMA = "PROMETEO_CONTEXT_SOURCE_INDEX_001"
REQUIRED_ALLOWED_FOR = "tl_chat_readonly_runtime"
REQUIRED_FIELDS = frozenset(
    {
        "articolo",
        "codice_articolo",
        "quantita",
        "data_spedizione",
        "priorita_cliente",
    }
)
DEFAULT_SOURCE_INDEX = Path(__file__).resolve().parents[3] / "memory" / "context_source_index.json"


@dataclass(frozen=True)
class CustomerDemandRuntimeAuthorization:
    authorized: bool
    reason: str
    source_id: str = SOURCE_ID
    structural_origin: str | None = None


def authorize_customer_demand_runtime(
    index_path: Path = DEFAULT_SOURCE_INDEX,
) -> CustomerDemandRuntimeAuthorization:
    """Authorize the dedicated read-only TL Chat binding before any DB connection."""
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_INDEX_UNAVAILABLE")

    if payload.get("schema") != EXPECTED_SCHEMA:
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_INDEX_SCHEMA_INVALID")

    sources = payload.get("sources")
    if not isinstance(sources, list):
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_INDEX_SOURCES_INVALID")

    matches = [source for source in sources if isinstance(source, dict) and source.get("id") == SOURCE_ID]
    if len(matches) != 1:
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_REGISTRATION_NOT_UNIQUE")

    source: dict[str, Any] = matches[0]
    if source.get("kind") != "database_registry":
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_KIND_NOT_AUTHORIZED")
    if source.get("access_mode") != "read_only":
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_ACCESS_MODE_NOT_READ_ONLY")
    if source.get("runtime_enabled") is not True:
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_RUNTIME_DISABLED")

    allowed_for = source.get("allowed_for")
    if not isinstance(allowed_for, list) or REQUIRED_ALLOWED_FOR not in allowed_for:
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_BINDING_NOT_AUTHORIZED")

    allowed_fields = source.get("allowed_fields")
    if not isinstance(allowed_fields, list) or set(allowed_fields) != REQUIRED_FIELDS:
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_FIELDS_NOT_AUTHORIZED")

    structural_origin = source.get("structural_origin")
    if structural_origin != "customer_demand":
        return CustomerDemandRuntimeAuthorization(False, "SOURCE_ORIGIN_INVALID")

    return CustomerDemandRuntimeAuthorization(
        True,
        "AUTHORIZED_READ_ONLY_TL_CHAT",
        structural_origin=structural_origin,
    )
