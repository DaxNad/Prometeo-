from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.ingest.article_specification_image_acquisition import (
    ArticleSpecificationImageAcquisitionResult,
    ImageAcquisitionStatus,
)
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeResult,
    process_structured_intake_payload,
)


ERROR_INVALID_ACQUISITION = "INVALID_ACQUISITION"
ERROR_ACQUISITION_NOT_EXTRACTED = "ACQUISITION_NOT_EXTRACTED"
ERROR_PARSER_RESULT_REQUIRED = "PARSER_RESULT_REQUIRED"
ERROR_EMPTY_PARSED_PAYLOADS = "EMPTY_PARSED_PAYLOADS"
ERROR_UNSAFE_SEMANTIC_STATUS = "UNSAFE_SEMANTIC_STATUS"
ERROR_WRITER_BOUNDARY_VIOLATION = "WRITER_BOUNDARY_VIOLATION"

EXPECTED_SEMANTIC_STATUS = "DA_VERIFICARE"


class ArticleSpecificationIntakeBindingStatus(str, Enum):
    BOUND = "BOUND"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ArticleSpecificationIntakeBindingResult:
    ok: bool
    status: ArticleSpecificationIntakeBindingStatus
    source_id: str
    semantic_status: str
    facade_results: tuple[StructuredIntakeFacadeResult, ...]
    writer_called: bool
    persisted: bool
    requires_review: bool
    error_code: str | None = None


def bind_article_specification_acquisition(
    acquisition: ArticleSpecificationImageAcquisitionResult,
) -> ArticleSpecificationIntakeBindingResult:
    validation_error = _validate_acquisition(acquisition)
    if validation_error is not None:
        return _rejected(acquisition, validation_error)

    parser_result = acquisition.parser_result
    assert parser_result is not None

    facade_results = tuple(
        process_structured_intake_payload(payload)
        for payload in parser_result.payloads
    )
    writer_called = any(result.writer_called for result in facade_results)
    if writer_called:
        return ArticleSpecificationIntakeBindingResult(
            ok=False,
            status=ArticleSpecificationIntakeBindingStatus.REJECTED,
            source_id=acquisition.source_id,
            semantic_status=EXPECTED_SEMANTIC_STATUS,
            facade_results=facade_results,
            writer_called=True,
            persisted=False,
            requires_review=True,
            error_code=ERROR_WRITER_BOUNDARY_VIOLATION,
        )

    return ArticleSpecificationIntakeBindingResult(
        ok=True,
        status=ArticleSpecificationIntakeBindingStatus.BOUND,
        source_id=acquisition.source_id,
        semantic_status=EXPECTED_SEMANTIC_STATUS,
        facade_results=facade_results,
        writer_called=False,
        persisted=False,
        requires_review=True,
    )


def _validate_acquisition(acquisition: Any) -> str | None:
    if not isinstance(acquisition, ArticleSpecificationImageAcquisitionResult):
        return ERROR_INVALID_ACQUISITION
    if not acquisition.ok or acquisition.status != ImageAcquisitionStatus.EXTRACTED:
        return ERROR_ACQUISITION_NOT_EXTRACTED

    parser_result = acquisition.parser_result
    if parser_result is None or not parser_result.ok:
        return ERROR_PARSER_RESULT_REQUIRED
    if not parser_result.payloads:
        return ERROR_EMPTY_PARSED_PAYLOADS
    if any(
        str(payload.get("semantic_status") or "").strip().upper()
        != EXPECTED_SEMANTIC_STATUS
        for payload in parser_result.payloads
    ):
        return ERROR_UNSAFE_SEMANTIC_STATUS
    return None


def _rejected(
    acquisition: Any,
    error_code: str,
) -> ArticleSpecificationIntakeBindingResult:
    source_id = (
        acquisition.source_id
        if isinstance(acquisition, ArticleSpecificationImageAcquisitionResult)
        else ""
    )
    return ArticleSpecificationIntakeBindingResult(
        ok=False,
        status=ArticleSpecificationIntakeBindingStatus.REJECTED,
        source_id=source_id,
        semantic_status=EXPECTED_SEMANTIC_STATUS,
        facade_results=(),
        writer_called=False,
        persisted=False,
        requires_review=True,
        error_code=error_code,
    )
