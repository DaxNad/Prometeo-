from __future__ import annotations

from app.services.tl_chat_context_resolver import (
    TLChatContextCandidate,
    resolve_tl_chat_context,
)


def _candidate(
    source_name: str,
    payload: dict,
    *,
    source_status: str = "DA_VERIFICARE",
    confidence: str = "DA_VERIFICARE",
    planner_eligible: bool = False,
    requires_tl_confirmation: bool = True,
) -> TLChatContextCandidate:
    return TLChatContextCandidate(
        source_name=source_name,
        source_status=source_status,
        confidence=confidence,
        payload=payload,
        planner_eligible=planner_eligible,
        requires_tl_confirmation=requires_tl_confirmation,
    )


def test_equal_operational_values_do_not_create_false_conflict():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            _candidate(
                "local_specs_metadata",
                {"codice": " ab-12514 ", "source": "local"},
                source_status="CERTO",
                confidence="CERTO",
                requires_tl_confirmation=False,
            ),
            _candidate(
                "article_summary",
                {"codice": "AB-12514", "source": "summary"},
            ),
        ],
    )

    assert resolved.selected_source == "local_specs_metadata"
    assert resolved.source_status == "CERTO"
    assert resolved.conflicts == ()


def test_one_materially_conflicting_field_is_declared():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            _candidate(
                "local_specs_metadata",
                {"codice": "AB-12514", "rev": "A"},
                source_status="CERTO",
                confidence="CERTO",
                planner_eligible=True,
                requires_tl_confirmation=False,
            ),
            _candidate(
                "article_summary",
                {"codice": "AB-12514", "rev": "B"},
            ),
        ],
    )

    assert resolved.selected_source == "local_specs_metadata"
    assert resolved.source_status == "SOURCE_AMBIGUOUS"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.requires_tl_confirmation is True
    assert resolved.planner_eligible is False
    assert resolved.can_promote is False
    assert tuple(item.field_name for item in resolved.conflicts) == ("rev",)
    assert resolved.conflicts[0].sources == (
        "local_specs_metadata",
        "article_summary",
    )


def test_multiple_conflicting_fields_are_sorted_deterministically():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            _candidate(
                "spec_intake_preview",
                {"codice": "AB-12514", "rev": "B", "quantita": 12},
                source_status="PREVIEW_ONLY",
            ),
            _candidate(
                "local_specs_metadata",
                {"codice": "AB-12514", "rev": "A", "quantita": 10},
                source_status="CERTO",
                confidence="CERTO",
                requires_tl_confirmation=False,
            ),
        ],
    )

    assert tuple(item.field_name for item in resolved.conflicts) == (
        "quantita",
        "rev",
    )
    assert resolved.source_status == "SOURCE_AMBIGUOUS"
    assert resolved.confidence == "DA_VERIFICARE"


def test_preview_participating_in_conflict_never_promotes():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            _candidate(
                "local_specs_metadata",
                {"disegno": "DWG-1"},
                source_status="CERTO",
                confidence="CERTO",
                planner_eligible=True,
                requires_tl_confirmation=False,
            ),
            _candidate(
                "spec_intake_preview",
                {"disegno": "DWG-2"},
                source_status="PREVIEW_ONLY",
                confidence="PREVIEW_ONLY",
                planner_eligible=True,
            ),
        ],
    )

    assert resolved.source_status == "SOURCE_AMBIGUOUS"
    assert resolved.confidence == "DA_VERIFICARE"
    assert resolved.requires_tl_confirmation is True
    assert resolved.can_promote is False
    assert resolved.planner_eligible is False


def test_provenance_metadata_differences_are_not_operational_conflicts():
    resolved = resolve_tl_chat_context(
        article="12514",
        candidates=[
            _candidate(
                "local_specs_metadata",
                {
                    "codice": "AB-12514",
                    "source_id": "local:12514",
                    "retrieved_at": "2026-07-13T10:00:00Z",
                },
                source_status="CERTO",
                confidence="CERTO",
                requires_tl_confirmation=False,
            ),
            _candidate(
                "article_summary",
                {
                    "codice": "AB-12514",
                    "source_id": "summary:12514",
                    "retrieved_at": "2026-07-13T10:01:00Z",
                },
            ),
        ],
    )

    assert resolved.conflicts == ()
    assert resolved.selected_source == "local_specs_metadata"
