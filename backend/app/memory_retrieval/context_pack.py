from __future__ import annotations

from dataclasses import dataclass

from backend.app.memory_retrieval.binding import EvidenceItem


CONFIDENCE_PRIORITY = {
    "CERTO": 0,
    "DA_VERIFICARE": 1,
    "INFERITO": 2,
}

SECTION_PRIORITY = {
    "FATTO": 0,
    "INFERENZA": 1,
    "DA_VERIFICARE": 2,
}


@dataclass(frozen=True)
class ContextPackItem:
    source_id: str
    source_path: str
    source_type: str
    authority: str
    confidence: str
    section: str
    text: str
    reason: str
    rank_reason: str


@dataclass(frozen=True)
class ContextPack:
    query: str | None
    items: list[ContextPackItem]
    total_candidates: int
    selected_count: int
    truncated: bool
    build_reason: str


def build_context_pack(
    evidence: list[EvidenceItem],
    query: str | None = None,
    max_items: int = 5,
    max_chars_per_item: int = 500,
) -> ContextPack:
    valid_candidates = [
        item for item in evidence if item.retrieval_allowed is True and item.sensitive is False
    ]
    total_candidates = len(valid_candidates)

    if not valid_candidates:
        return ContextPack(
            query=query,
            items=[],
            total_candidates=0,
            selected_count=0,
            truncated=False,
            build_reason=_build_reason(max_items=max_items, total_candidates=0),
        )

    if max_items <= 0:
        return ContextPack(
            query=query,
            items=[],
            total_candidates=total_candidates,
            selected_count=0,
            truncated=True,
            build_reason=_build_reason(max_items=max_items, total_candidates=total_candidates),
        )

    ranked = sorted(valid_candidates, key=_rank_key)
    selected = ranked[:max_items]
    items = [
        ContextPackItem(
            source_id=item.source_id,
            source_path=item.source_path,
            source_type=item.source_type,
            authority=item.authority,
            confidence=item.confidence,
            section=item.section,
            text=_limit_text(item.text, max_chars_per_item),
            reason=item.reason,
            rank_reason=_rank_reason(item),
        )
        for item in selected
    ]

    return ContextPack(
        query=query,
        items=items,
        total_candidates=total_candidates,
        selected_count=len(items),
        truncated=total_candidates > len(items),
        build_reason=_build_reason(max_items=max_items, total_candidates=total_candidates),
    )


def _rank_key(item: EvidenceItem) -> tuple[int, int, str, str]:
    return (
        CONFIDENCE_PRIORITY.get(item.confidence, len(CONFIDENCE_PRIORITY)),
        SECTION_PRIORITY.get(item.section, len(SECTION_PRIORITY)),
        item.source_path,
        item.source_id,
    )


def _limit_text(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}..."


def _rank_reason(item: EvidenceItem) -> str:
    return (
        "Included after retrieval/sensitive filters; ranked by confidence "
        f"{item.confidence}, section {item.section}, source_path and source_id."
    )


def _build_reason(max_items: int, total_candidates: int) -> str:
    return (
        "Filtered EvidenceItem candidates by retrieval_allowed true and sensitive false; "
        "ordered by confidence, section, source_path and source_id; "
        f"limited to max_items={max_items} from total_candidates={total_candidates}."
    )
