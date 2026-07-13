from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.services.customer_demand_readonly_reader import read_customer_demand
from app.services.customer_demand_runtime_authorization import (
    CustomerDemandRuntimeAuthorization,
    authorize_customer_demand_runtime,
)
from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    TLChatResolvedContext,
    resolve_tl_chat_context,
)

ReaderCallable = Callable[..., dict[str, Any]]
AuthorizerCallable = Callable[[], CustomerDemandRuntimeAuthorization]


def build_customer_demand_candidate(
    *,
    articolo: str | None = None,
    codice_articolo: str | None = None,
    limit: int = 50,
    reader: ReaderCallable = read_customer_demand,
    authorizer: AuthorizerCallable = authorize_customer_demand_runtime,
) -> TLChatContextCandidate:
    """Authorize first, then build one governed read-only customer-demand candidate."""
    authorization = authorizer()
    if not authorization.authorized:
        return TLChatContextCandidate(
            source_name="customer_demand_registry",
            source_status="SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
            confidence="DA_VERIFICARE",
            payload={
                "source_id": "customer_demand_registry",
                "authorization_reason": authorization.reason,
                "records": [],
                "missing_data": ["customer_demand_runtime_not_authorized"],
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    try:
        result = reader(
            articolo=articolo,
            codice_articolo=codice_articolo,
            limit=limit,
        )
    except Exception as exc:
        return TLChatContextCandidate(
            source_name="customer_demand_registry",
            source_status="SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
            confidence="DA_VERIFICARE",
            payload={
                "source_id": "customer_demand_registry",
                "error_type": exc.__class__.__name__,
                "records": [],
                "missing_data": ["customer_demand_reader_unavailable"],
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    return TLChatContextCandidate(
        source_name="customer_demand_registry",
        source_status=str(result.get("source_status") or "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"),
        confidence=str(result.get("confidence") or "DA_VERIFICARE"),
        payload=dict(result),
        planner_eligible=False,
        requires_tl_confirmation=True,
    )


def resolve_customer_demand_context(
    *,
    articolo: str | None = None,
    codice_articolo: str | None = None,
    limit: int = 50,
    reader: ReaderCallable = read_customer_demand,
    authorizer: AuthorizerCallable = authorize_customer_demand_runtime,
) -> TLChatResolvedContext:
    candidate = build_customer_demand_candidate(
        articolo=articolo,
        codice_articolo=codice_articolo,
        limit=limit,
        reader=reader,
        authorizer=authorizer,
    )
    resolver_article = articolo or codice_articolo or ""
    return resolve_tl_chat_context(article=resolver_article, candidates=[candidate])
