from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SOURCE_PRIORITY: dict[str, int] = {
    "local_specs_metadata": 10,
    "article_summary": 20,
    "lifecycle_registry": 30,
    "customer_demand_registry": 35,
    "spec_intake_preview": 40,
    "route_matrix_preview": 50,
    "context_source_reader_adapter": 60,
    "context_source_index": 70,
    "missing": 999,
}

TL_CONTEXT_RETRIEVAL_SOURCE_STATUSES = frozenset(
    {
        "SOURCE_FOUND",
        "SOURCE_MISSING",
        "SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
        "SOURCE_FORBIDDEN",
        "SOURCE_AMBIGUOUS",
        "PATH_TRAVERSAL_BLOCKED",
    }
)

LEGACY_SOURCE_STATUSES = frozenset(
    {
        "CERTO",
        "ATTIVO",
        "PREVIEW_ONLY",
        "DA_VERIFICARE",
        "INFERITO",
        "MISSING",
    }
)

UNCERTAIN_SOURCE_STATUSES = frozenset(
    {
        "PREVIEW_ONLY",
        "DA_VERIFICARE",
        "INFERITO",
        "MISSING",
        "SOURCE_MISSING",
        "SOURCE_AUTHORIZED_BUT_UNAVAILABLE",
        "SOURCE_FORBIDDEN",
        "SOURCE_AMBIGUOUS",
        "PATH_TRAVERSAL_BLOCKED",
    }
)

NON_OPERATIONAL_PAYLOAD_FIELDS = frozenset(
    {
        "source",
        "source_id",
        "source_name",
        "source_type",
        "source_status",
        "confidence",
        "semantic_status",
        "authority_rank",
        "reason",
        "authorization_reason",
        "retrieved_at",
        "structural_origin",
        "runtime_binding",
        "planner_eligible",
        "requires_tl_confirmation",
        "can_promote",
        "missing_data",
        "error_type",
    }
)


@dataclass(frozen=True)
class TLChatContextCandidate:
    source_name: str
    source_status: str
    confidence: str
    payload: dict[str, Any]
    planner_eligible: bool = False
    requires_tl_confirmation: bool = True


@dataclass(frozen=True)
class TLChatContextConflict:
    field_name: str
    sources: tuple[str, ...]
    values: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class TLChatResolvedContext:
    article: str
    selected_source: str
    source_status: str
    confidence: str
    planner_eligible: bool
    requires_tl_confirmation: bool
    can_promote: bool
    reason: str
    payload: dict[str, Any]
    conflicts: tuple[TLChatContextConflict, ...] = ()


def _normalize_article(value: str | None) -> str:
    return str(value or "").strip().upper()


def _normalize_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip().upper()
    return text or fallback


def _normalize_source_status(value: Any) -> str:
    source_status = _normalize_text(value, "DA_VERIFICARE")
    if source_status in TL_CONTEXT_RETRIEVAL_SOURCE_STATUSES:
        return source_status
    if source_status in LEGACY_SOURCE_STATUSES:
        return source_status
    return "DA_VERIFICARE"


def _priority(candidate: TLChatContextCandidate) -> int:
    return SOURCE_PRIORITY.get(candidate.source_name, SOURCE_PRIORITY["missing"])


def _is_preview_or_uncertain(candidate: TLChatContextCandidate) -> bool:
    return (
        _normalize_source_status(candidate.source_status) in UNCERTAIN_SOURCE_STATUSES
        or candidate.confidence in {"PREVIEW_ONLY", "DA_VERIFICARE", "INFERITO"}
        or candidate.requires_tl_confirmation
    )


def _canonicalize_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().upper()
    if isinstance(value, dict):
        return tuple(
            (str(key), _canonicalize_value(item))
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )
    if isinstance(value, (list, tuple)):
        return tuple(_canonicalize_value(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted((_canonicalize_value(item) for item in value), key=repr))
    return value


def _detect_conflicts(
    candidates: list[TLChatContextCandidate],
) -> tuple[TLChatContextConflict, ...]:
    ordered_candidates = sorted(candidates, key=lambda item: (_priority(item), item.source_name))
    field_values: dict[str, list[tuple[str, Any, Any]]] = {}

    for candidate in ordered_candidates:
        for field_name, raw_value in candidate.payload.items():
            normalized_field = str(field_name).strip()
            if not normalized_field or normalized_field in NON_OPERATIONAL_PAYLOAD_FIELDS:
                continue
            field_values.setdefault(normalized_field, []).append(
                (
                    candidate.source_name,
                    raw_value,
                    _canonicalize_value(raw_value),
                )
            )

    conflicts: list[TLChatContextConflict] = []
    for field_name in sorted(field_values):
        values = field_values[field_name]
        if len(values) < 2:
            continue
        if len({repr(canonical_value) for _, _, canonical_value in values}) < 2:
            continue
        conflicts.append(
            TLChatContextConflict(
                field_name=field_name,
                sources=tuple(dict.fromkeys(source_name for source_name, _, _ in values)),
                values=tuple((source_name, raw_value) for source_name, raw_value, _ in values),
            )
        )

    return tuple(conflicts)


def resolve_tl_chat_context(
    *,
    article: str,
    candidates: list[TLChatContextCandidate],
) -> TLChatResolvedContext:
    """
    Deterministic TL Chat context resolver.

    Contract:
    - orders already-authorized source candidates
    - compares overlapping operational fields without reconciling conflicts
    - does not read files
    - does not write files
    - does not call LLMs
    - does not call planner, SMF, DB, ATLAS Engine or frontend
    - never promotes uncertain, preview or conflicting sources to CERTO
    """
    safe_article = _normalize_article(article)

    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate.source_name in SOURCE_PRIORITY
    ]

    if not valid_candidates:
        return TLChatResolvedContext(
            article=safe_article,
            selected_source="missing",
            source_status="MISSING",
            confidence="DA_VERIFICARE",
            planner_eligible=False,
            requires_tl_confirmation=True,
            can_promote=False,
            reason="nessuna fonte ammessa disponibile per articolo",
            payload={},
        )

    selected = sorted(valid_candidates, key=_priority)[0]
    conflicts = _detect_conflicts(valid_candidates)

    if conflicts:
        conflicting_fields = ", ".join(conflict.field_name for conflict in conflicts)
        return TLChatResolvedContext(
            article=safe_article,
            selected_source=selected.source_name,
            source_status="SOURCE_AMBIGUOUS",
            confidence="DA_VERIFICARE",
            planner_eligible=False,
            requires_tl_confirmation=True,
            can_promote=False,
            reason=f"conflitto tra fonti autorizzate sui campi: {conflicting_fields}",
            payload=dict(selected.payload),
            conflicts=conflicts,
        )

    source_status = _normalize_source_status(selected.source_status)
    confidence = _normalize_text(selected.confidence, "DA_VERIFICARE")

    can_promote = (
        source_status == "CERTO"
        and confidence == "CERTO"
        and selected.requires_tl_confirmation is False
    )

    if _is_preview_or_uncertain(selected):
        can_promote = False

    return TLChatResolvedContext(
        article=safe_article,
        selected_source=selected.source_name,
        source_status=source_status,
        confidence=confidence,
        planner_eligible=bool(selected.planner_eligible) if can_promote else False,
        requires_tl_confirmation=bool(selected.requires_tl_confirmation),
        can_promote=can_promote,
        reason=f"fonte selezionata per priorità: {selected.source_name}",
        payload=dict(selected.payload),
    )
