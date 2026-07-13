from __future__ import annotations

from app.services.customer_demand_context_resolver_binding import (
    build_customer_demand_candidate,
    resolve_customer_demand_context,
)
from app.services.customer_demand_readonly_reader import _statement_for_connection
from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    resolve_tl_chat_context,
)


def _reader_result(records):
    return {
        "source_id": "customer_demand_registry",
        "structural_origin": "customer_demand",
        "retrieved_at": "2026-07-13T10:00:00+00:00",
        "source_status": "SOURCE_FOUND",
        "runtime_binding": "TL_CHAT_READ_ONLY",
        "lookup": {"field": "articolo", "value": "12514", "limit": 50},
        "records": records,
        "freshness": "UNKNOWN",
        "semantic_status": "DA_VERIFICARE",
        "confidence": "DA_VERIFICARE",
        "missing_data": [] if records else ["record_customer_demand_not_found"],
    }


def test_binding_resolves_reader_output_without_promotion():
    calls = []

    def reader(**kwargs):
        calls.append(kwargs)
        return _reader_result([{"articolo": "12514"}])

    resolved = resolve_customer_demand_context(articolo="12514", reader=reader)

    assert calls == [{"articolo": "12514", "codice_articolo": None, "limit": 50}]
    assert resolved.selected_source == "customer_demand_registry"
    assert resolved.source_status == "SOURCE_FOUND"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.payload["freshness"] == "UNKNOWN"
    assert resolved.payload["records"] == [{"articolo": "12514"}]
    assert resolved.payload["runtime_binding"] == "TL_CHAT_READ_ONLY"
    assert resolved.payload["structural_origin"] == "customer_demand"
    assert resolved.planner_eligible is False
    assert resolved.requires_tl_confirmation is True
    assert resolved.can_promote is False


def test_binding_preserves_empty_record_semantics():
    resolved = resolve_customer_demand_context(
        codice_articolo="MISSING",
        reader=lambda **kwargs: _reader_result([]),
    )
    assert resolved.source_status == "SOURCE_FOUND"
    assert resolved.payload["records"] == []
    assert resolved.payload["missing_data"] == ["record_customer_demand_not_found"]


def test_binding_maps_reader_failure_to_authorized_but_unavailable():
    def failing_reader(**kwargs):
        raise RuntimeError("database unavailable")

    candidate = build_customer_demand_candidate(articolo="12514", reader=failing_reader)
    assert candidate.source_status == "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"
    assert candidate.payload["records"] == []
    assert candidate.payload["missing_data"] == ["customer_demand_reader_unavailable"]
    assert "database unavailable" not in str(candidate.payload)


def test_customer_demand_priority_precedes_preview_but_not_authoritative_sources():
    demand = TLChatContextCandidate(
        source_name="customer_demand_registry",
        source_status="SOURCE_FOUND",
        confidence="DA_VERIFICARE",
        payload={"source_id": "customer_demand_registry"},
    )
    preview = TLChatContextCandidate(
        source_name="spec_intake_preview",
        source_status="PREVIEW_ONLY",
        confidence="PREVIEW_ONLY",
        payload={},
    )
    authoritative = TLChatContextCandidate(
        source_name="article_summary",
        source_status="CERTO",
        confidence="CERTO",
        payload={},
        requires_tl_confirmation=False,
    )

    selected_without_authoritative = resolve_tl_chat_context(
        article="12514", candidates=[preview, demand]
    )
    selected_with_authoritative = resolve_tl_chat_context(
        article="12514", candidates=[preview, demand, authoritative]
    )

    assert selected_without_authoritative.selected_source == "customer_demand_registry"
    assert selected_with_authoritative.selected_source == "article_summary"


def test_sqlite_placeholder_adaptation_is_local_and_bounded():
    SQLiteConnection = type("Connection", (), {"__module__": "sqlite3"})
    statement = "SELECT * FROM customer_demand WHERE articolo = %s LIMIT %s"
    assert _statement_for_connection(SQLiteConnection(), statement) == (
        "SELECT * FROM customer_demand WHERE articolo = ? LIMIT ?"
    )
