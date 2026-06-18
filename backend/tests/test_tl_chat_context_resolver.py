from __future__ import annotations

from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    resolve_tl_chat_context,
)


def test_tl_chat_context_resolver_returns_missing_without_candidates():
    resolved = resolve_tl_chat_context(article="99999", candidates=[])

    assert resolved.article == "99999"
    assert resolved.selected_source == "missing"
    assert resolved.source_status == "MISSING"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.planner_eligible is False
    assert resolved.requires_tl_confirmation is True
    assert resolved.can_promote is False


def test_tl_chat_context_resolver_selects_spec_intake_preview_for_12514():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            TLChatContextCandidate(
                source_name="spec_intake_preview",
                source_status="PREVIEW_ONLY",
                confidence="DA_VERIFICARE",
                planner_eligible=False,
                requires_tl_confirmation=True,
                payload={"article": "12514"},
            )
        ],
    )

    assert resolved.article == "12514"
    assert resolved.selected_source == "spec_intake_preview"
    assert resolved.source_status == "PREVIEW_ONLY"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.planner_eligible is False
    assert resolved.requires_tl_confirmation is True
    assert resolved.can_promote is False


def test_tl_chat_context_resolver_lifecycle_beats_spec_intake_preview():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            TLChatContextCandidate(
                source_name="spec_intake_preview",
                source_status="PREVIEW_ONLY",
                confidence="DA_VERIFICARE",
                payload={"source": "preview"},
            ),
            TLChatContextCandidate(
                source_name="lifecycle_registry",
                source_status="DA_VERIFICARE",
                confidence="DA_VERIFICARE",
                payload={"source": "lifecycle"},
            ),
        ],
    )

    assert resolved.selected_source == "lifecycle_registry"
    assert resolved.payload["source"] == "lifecycle"
    assert resolved.can_promote is False


def test_tl_chat_context_resolver_local_specs_metadata_beats_lifecycle():
    resolved = resolve_tl_chat_context(
        article="12066",
        candidates=[
            TLChatContextCandidate(
                source_name="lifecycle_registry",
                source_status="ATTIVO",
                confidence="INFERITO",
                payload={"source": "lifecycle"},
            ),
            TLChatContextCandidate(
                source_name="local_specs_metadata",
                source_status="CERTO",
                confidence="CERTO",
                planner_eligible=True,
                requires_tl_confirmation=False,
                payload={"source": "local_specs"},
            ),
        ],
    )

    assert resolved.selected_source == "local_specs_metadata"
    assert resolved.payload["source"] == "local_specs"
    assert resolved.confidence == "CERTO"
    assert resolved.can_promote is True
    assert resolved.planner_eligible is True


def test_tl_chat_context_resolver_never_promotes_preview_to_certo():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            TLChatContextCandidate(
                source_name="spec_intake_preview",
                source_status="PREVIEW_ONLY",
                confidence="CERTO",
                planner_eligible=True,
                requires_tl_confirmation=True,
                payload={},
            )
        ],
    )

    assert resolved.selected_source == "spec_intake_preview"
    assert resolved.source_status == "PREVIEW_ONLY"
    assert resolved.can_promote is False
    assert resolved.planner_eligible is False


def test_tl_chat_context_resolver_ignores_unknown_source_names():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            TLChatContextCandidate(
                source_name="unauthorized_runtime_source",
                source_status="CERTO",
                confidence="CERTO",
                planner_eligible=True,
                requires_tl_confirmation=False,
                payload={"unsafe": True},
            )
        ],
    )

    assert resolved.selected_source == "missing"
    assert resolved.can_promote is False
    assert resolved.payload == {}
