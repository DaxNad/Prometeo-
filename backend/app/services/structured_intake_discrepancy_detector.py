from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.domain.article_operational_registry import get_operational_registry_entry
from app.domain.operational_class import normalize_operational_class
from app.services.intake_destination_classifier import IntakeItem


SUPPORTED_FIELD = "operational_class"
COMPARISON_RULE = "OPERATIONAL_CLASS_CANONICAL_EQUALITY"
AUTHORITATIVE_SOURCE_ID_PREFIX = "article_operational_registry"


class IntakeDiscrepancyStatus(str, Enum):
    NO_AUTHORITATIVE_RECORD = "NO_AUTHORITATIVE_RECORD"
    CONSISTENT_WITH_AUTHORITATIVE = "CONSISTENT_WITH_AUTHORITATIVE"
    DISCREPANCY_DETECTED = "DISCREPANCY_DETECTED"
    COMPARISON_NOT_SUPPORTED = "COMPARISON_NOT_SUPPORTED"
    AUTHORITATIVE_READ_FAILED = "AUTHORITATIVE_READ_FAILED"


@dataclass(frozen=True)
class StructuredIntakeDiscrepancyResult:
    status: IntakeDiscrepancyStatus
    article: str
    field_name: str
    comparison_performed: bool
    discrepancy_detected: bool
    authoritative_value: str | None
    incoming_value: str
    authoritative_semantic_status: str | None
    incoming_semantic_status: str | None
    authoritative_source: str | None
    incoming_source_id: str
    requires_review: bool
    persistence_allowed: bool | None
    authoritative_source_id: str | None = None
    authoritative_source_authority: str | None = None
    incoming_authority_role: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    review_reason: str = ""
    comparison_rule: str = COMPARISON_RULE


def detect_structured_intake_discrepancy(
    item: IntakeItem,
    *,
    authoritative_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
) -> StructuredIntakeDiscrepancyResult:
    article = _article_from_item(item)
    field_name = _normalize_field_name(item.field_name)
    incoming_value = _normalize_token(item.value)
    incoming_semantic_status = _optional_token(item.semantic_status)
    incoming_requires_review = incoming_semantic_status != "CERTO"

    if field_name != SUPPORTED_FIELD:
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.COMPARISON_NOT_SUPPORTED,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            requires_review=incoming_requires_review,
            review_reason="Comparison is not supported for this field.",
        )

    if not article:
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.NO_AUTHORITATIVE_RECORD,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            incoming_requires_review=incoming_requires_review,
            review_reason="No authoritative operational class is available.",
        )

    reader = authoritative_reader or get_operational_registry_entry
    try:
        record = reader(article)
    except (OSError, json.JSONDecodeError):
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.AUTHORITATIVE_READ_FAILED,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            requires_review=True,
            persistence_allowed=False,
            blocking_reasons=(
                IntakeDiscrepancyStatus.AUTHORITATIVE_READ_FAILED.value,
            ),
            review_reason="Authoritative operational registry read failed.",
        )

    if record is None:
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.NO_AUTHORITATIVE_RECORD,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            incoming_requires_review=incoming_requires_review,
            review_reason="No authoritative operational class is available.",
        )

    if not isinstance(record, Mapping):
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.AUTHORITATIVE_READ_FAILED,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            requires_review=True,
            persistence_allowed=False,
            blocking_reasons=(
                IntakeDiscrepancyStatus.AUTHORITATIVE_READ_FAILED.value,
            ),
            review_reason="Authoritative operational registry read failed.",
        )

    raw_authoritative_value = _optional_text(record.get(SUPPORTED_FIELD))
    if raw_authoritative_value is None:
        return _result(
            item=item,
            status=IntakeDiscrepancyStatus.NO_AUTHORITATIVE_RECORD,
            article=article,
            field_name=field_name,
            incoming_value=incoming_value,
            incoming_requires_review=incoming_requires_review,
            record=record,
            review_reason="The authoritative record has no operational class.",
        )

    authoritative_value = _normalize_token(raw_authoritative_value)
    discrepancy_detected = normalize_operational_class(
        incoming_value
    ) != normalize_operational_class(authoritative_value)
    status = (
        IntakeDiscrepancyStatus.DISCREPANCY_DETECTED
        if discrepancy_detected
        else IntakeDiscrepancyStatus.CONSISTENT_WITH_AUTHORITATIVE
    )
    review_reason = (
        f"Article {article} operational_class discrepancy: authoritative "
        f"{authoritative_value}, incoming {incoming_value}."
        if discrepancy_detected
        else "Incoming operational class is consistent with the authoritative record."
    )

    return _result(
        item=item,
        status=status,
        article=article,
        field_name=field_name,
        comparison_performed=True,
        discrepancy_detected=discrepancy_detected,
        authoritative_value=authoritative_value,
        incoming_value=incoming_value,
        requires_review=discrepancy_detected or incoming_requires_review,
        persistence_allowed=False if discrepancy_detected else None,
        blocking_reasons=(status.value,) if discrepancy_detected else (),
        record=record,
        review_reason=review_reason,
    )


def _result(
    *,
    item: IntakeItem,
    status: IntakeDiscrepancyStatus,
    article: str,
    field_name: str,
    incoming_value: str,
    comparison_performed: bool = False,
    discrepancy_detected: bool = False,
    authoritative_value: str | None = None,
    requires_review: bool | None = None,
    persistence_allowed: bool | None = None,
    incoming_requires_review: bool | None = None,
    record: Mapping[str, Any] | None = None,
    blocking_reasons: tuple[str, ...] = (),
    review_reason: str = "",
) -> StructuredIntakeDiscrepancyResult:
    record = record or {}
    incoming_semantic_status = _optional_token(item.semantic_status)
    if requires_review is None:
        requires_review = (
            incoming_requires_review
            if incoming_requires_review is not None
            else incoming_semantic_status != "CERTO"
        )
    return StructuredIntakeDiscrepancyResult(
        status=status,
        article=article,
        field_name=field_name,
        comparison_performed=comparison_performed,
        discrepancy_detected=discrepancy_detected,
        authoritative_value=authoritative_value,
        incoming_value=incoming_value,
        authoritative_semantic_status=_authoritative_semantic_status(record),
        incoming_semantic_status=incoming_semantic_status,
        authoritative_source=_optional_text(record.get("source")),
        incoming_source_id=item.source_id,
        requires_review=requires_review,
        persistence_allowed=persistence_allowed,
        authoritative_source_id=(
            _authoritative_source_id(article)
            if article
            and status != IntakeDiscrepancyStatus.COMPARISON_NOT_SUPPORTED
            else None
        ),
        authoritative_source_authority=_optional_token(
            record.get("source_authority")
        ),
        incoming_authority_role=_optional_token(item.authority_role),
        blocking_reasons=blocking_reasons,
        review_reason=review_reason,
    )


def _article_from_item(item: IntakeItem) -> str:
    for container in (item.context, item.value if isinstance(item.value, Mapping) else None):
        if not isinstance(container, Mapping):
            continue
        for key in ("article", "articolo", "entity_id"):
            article = _normalize_token(container.get(key))
            if article:
                return article
    return ""


def _authoritative_semantic_status(record: Mapping[str, Any]) -> str | None:
    direct = _optional_token(record.get("semantic_status"))
    if direct is not None:
        return direct
    source_evidence = record.get("source_evidence")
    if isinstance(source_evidence, Mapping):
        return _optional_token(source_evidence.get("semantic_status"))
    return None


def _authoritative_source_id(article: str) -> str:
    return f"{AUTHORITATIVE_SOURCE_ID_PREFIX}:{article}"


def _normalize_field_name(value: Any) -> str:
    return re.sub(r"[\s-]+", "_", str(value or "").strip().casefold())


def _normalize_token(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _optional_token(value: Any) -> str | None:
    normalized = _normalize_token(value)
    return normalized or None


def _optional_text(value: Any) -> str | None:
    cleaned = str(value or "").strip()
    return cleaned or None
