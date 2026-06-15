from __future__ import annotations

import sys

from backend.app.memory_retrieval.binding import EvidenceItem
from backend.app.memory_retrieval.context_pack import ContextPack, build_context_pack


def _evidence(**overrides) -> EvidenceItem:
    fields = {
        "source_id": "MEMORY_TEST",
        "source_path": "memory/domain/invariants.md",
        "source_type": "domain_invariant",
        "authority": "governed_memory",
        "confidence": "CERTO",
        "section": "FATTO",
        "text": "ZAW1 e ZAW2 non sono intercambiabili.",
        "reason": "Included FATTO section from retrievable memory file.",
        "retrieval_allowed": True,
        "sensitive": False,
    }
    fields.update(overrides)
    return EvidenceItem(**fields)


def test_empty_context_pack_when_evidence_is_empty():
    pack = build_context_pack([], query="ZAW2")

    assert pack == ContextPack(
        query="ZAW2",
        items=[],
        total_candidates=0,
        selected_count=0,
        truncated=False,
        build_reason=(
            "Filtered EvidenceItem candidates by retrieval_allowed true and sensitive false; "
            "ordered by confidence, section, source_path and source_id; "
            "limited to max_items=5 from total_candidates=0."
        ),
    )


def test_excludes_retrieval_not_allowed():
    pack = build_context_pack([_evidence(retrieval_allowed=False)])

    assert pack.items == []
    assert pack.total_candidates == 0


def test_excludes_sensitive_items():
    pack = build_context_pack([_evidence(sensitive=True)])

    assert pack.items == []
    assert pack.total_candidates == 0


def test_orders_by_confidence_priority():
    pack = build_context_pack(
        [
            _evidence(source_id="INFERITO", confidence="INFERITO"),
            _evidence(source_id="CERTO", confidence="CERTO"),
            _evidence(source_id="DA_VERIFICARE", confidence="DA_VERIFICARE"),
        ]
    )

    assert [item.source_id for item in pack.items] == ["CERTO", "DA_VERIFICARE", "INFERITO"]


def test_orders_sections_with_same_confidence():
    pack = build_context_pack(
        [
            _evidence(source_id="VERIFY", section="DA_VERIFICARE"),
            _evidence(source_id="INFERENCE", section="INFERENZA"),
            _evidence(source_id="FACT", section="FATTO"),
        ]
    )

    assert [item.section for item in pack.items] == ["FATTO", "INFERENZA", "DA_VERIFICARE"]


def test_order_is_stable_by_source_path_and_source_id():
    pack = build_context_pack(
        [
            _evidence(source_id="B", source_path="memory/b.md"),
            _evidence(source_id="A2", source_path="memory/a.md"),
            _evidence(source_id="A1", source_path="memory/a.md"),
        ]
    )

    assert [(item.source_path, item.source_id) for item in pack.items] == [
        ("memory/a.md", "A1"),
        ("memory/a.md", "A2"),
        ("memory/b.md", "B"),
    ]


def test_respects_max_items_and_sets_truncated():
    pack = build_context_pack(
        [
            _evidence(source_id="A"),
            _evidence(source_id="B"),
            _evidence(source_id="C"),
        ],
        max_items=2,
    )

    assert [item.source_id for item in pack.items] == ["A", "B"]
    assert pack.total_candidates == 3
    assert pack.selected_count == 2
    assert pack.truncated is True


def test_max_items_zero_returns_empty_items_and_truncated_when_candidates_exist():
    pack = build_context_pack([_evidence()], max_items=0)

    assert pack.items == []
    assert pack.total_candidates == 1
    assert pack.selected_count == 0
    assert pack.truncated is True


def test_truncates_text_over_max_chars():
    pack = build_context_pack([_evidence(text="abcdef")], max_chars_per_item=3)

    assert pack.items[0].text == "abc..."


def test_max_chars_zero_produces_empty_text():
    pack = build_context_pack([_evidence(text="abcdef")], max_chars_per_item=0)

    assert pack.items[0].text == ""


def test_preserves_authority_confidence_and_source_fields():
    pack = build_context_pack(
        [
            _evidence(
                source_id="MEMORY_SOURCE",
                source_path="memory/retrieval/policy.md",
                source_type="retrieval_policy",
                authority="tl_confirmed_summary",
                confidence="DA_VERIFICARE",
                section="INFERENZA",
            )
        ]
    )

    item = pack.items[0]
    assert item.source_id == "MEMORY_SOURCE"
    assert item.source_path == "memory/retrieval/policy.md"
    assert item.source_type == "retrieval_policy"
    assert item.authority == "tl_confirmed_summary"
    assert item.confidence == "DA_VERIFICARE"
    assert item.section == "INFERENZA"
    assert item.reason == "Included FATTO section from retrievable memory file."
    assert "ranked by confidence DA_VERIFICARE" in item.rank_reason


def test_does_not_import_runtime_modules_or_planner():
    forbidden_modules = (
        "backend.app.api.tl_chat",
        "backend.app.atlas_engine.governed_retrieval",
        "backend.app.services.sequence_planner",
        "backend.app.services.planner_smf",
    )
    for module in forbidden_modules:
        sys.modules.pop(module, None)

    build_context_pack([_evidence()])

    for module in forbidden_modules:
        assert module not in sys.modules
