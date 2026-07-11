from __future__ import annotations

import pytest

from app.services.intake_destination_classifier import IntakeItem
from app.services.structured_intake_discrepancy_detector import (
    IntakeDiscrepancyStatus,
    detect_structured_intake_discrepancy,
)


ARTICLE = "99878"


def _item(
    *,
    field_name: str = "operational_class",
    value: str = "STANDARD",
    article: str = ARTICLE,
) -> IntakeItem:
    return IntakeItem(
        field_name=field_name,
        value=value,
        source_id=f"preview:synthetic-discrepancy:{ARTICLE}",
        source_type="spec_intake_preview",
        source_status="SOURCE_FOUND",
        semantic_status="DA_VERIFICARE",
        authority_role="OPERATORE",
        context={"article": article} if article else {},
        metadata={},
    )


def test_consistent_value_uses_canonical_operational_class_normalization():
    result = detect_structured_intake_discrepancy(
        _item(value="spare-part"),
        authoritative_reader=lambda _article: {
            "operational_class": "RICAMBIO",
            "semantic_status": "CERTO",
            "source": "human_operational_confirmation",
        },
    )

    assert result.status == IntakeDiscrepancyStatus.CONSISTENT_WITH_AUTHORITATIVE
    assert result.comparison_performed is True
    assert result.discrepancy_detected is False
    assert result.authoritative_value == "RICAMBIO"
    assert result.incoming_value == "SPARE_PART"
    assert result.persistence_allowed is None


def test_missing_authoritative_record_is_reported_without_persistence_decision():
    result = detect_structured_intake_discrepancy(
        _item(),
        authoritative_reader=lambda _article: None,
    )

    assert result.status == IntakeDiscrepancyStatus.NO_AUTHORITATIVE_RECORD
    assert result.comparison_performed is False
    assert result.discrepancy_detected is False
    assert result.authoritative_value is None
    assert result.persistence_allowed is None


def test_unsupported_field_does_not_read_authoritative_registry():
    result = detect_structured_intake_discrepancy(
        _item(field_name="drawing", value="SYNTHETIC-DRAWING"),
        authoritative_reader=lambda _article: pytest.fail(
            "authoritative registry read for unsupported field"
        ),
    )

    assert result.status == IntakeDiscrepancyStatus.COMPARISON_NOT_SUPPORTED
    assert result.comparison_performed is False
    assert result.discrepancy_detected is False
    assert result.persistence_allowed is None


def test_authoritative_read_failure_blocks_persistence():
    def fail_read(_article: str):
        raise OSError("synthetic registry read failure")

    result = detect_structured_intake_discrepancy(
        _item(),
        authoritative_reader=fail_read,
    )

    assert result.status == IntakeDiscrepancyStatus.AUTHORITATIVE_READ_FAILED
    assert result.comparison_performed is False
    assert result.discrepancy_detected is False
    assert result.requires_review is True
    assert result.persistence_allowed is False


def test_missing_article_does_not_read_authoritative_registry():
    result = detect_structured_intake_discrepancy(
        _item(article=""),
        authoritative_reader=lambda _article: pytest.fail(
            "authoritative registry read without article"
        ),
    )

    assert result.status == IntakeDiscrepancyStatus.NO_AUTHORITATIVE_RECORD
    assert result.comparison_performed is False
    assert result.discrepancy_detected is False
    assert result.persistence_allowed is None
