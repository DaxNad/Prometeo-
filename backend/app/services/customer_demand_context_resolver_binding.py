from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.services.customer_demand_readonly_reader import read_customer_demand
from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    TLChatResolvedContext,
    resolve_tl_chat_context,
)

ReaderCallable = Callable[..., dict[str, Any]]


def build_customer_demand_candidate(
    *,
    articolo: str | None = None,
    codice_articolo: str | None = None,
    limit: int = 50,
    reader: ReaderCallable = read_customer_demand,
) -> TLChatContextCandidate:
    """Build one governed resolver candidate from the read-only registry reader."""
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
        confidence="DA_VERIFICARE",
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
) -> TLChatResolvedContext:
    """Resolve only the customer-demand candidate; no TL Chat or API binding occurs here."""
    candidate = build_customer_demand_candidate(
        articolo=articolo,
        codice_articolo=codice_articolo,
        limit=limit,
        reader=reader,
    )
    resolver_article = articolo or codice_articolo or ""
    return resolve_tl_chat_context(
        article=resolver_article,
        candidates=[candidate],
    )
