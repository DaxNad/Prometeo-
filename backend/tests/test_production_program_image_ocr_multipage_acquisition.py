from __future__ import annotations

from dataclasses import dataclass

import pytest

import app.ingest.production_program_image_ocr_acquisition as acquisition
from app.ingest.production_program_image_ocr_acquisition import (
    OCRTextExtractionResult,
    ProductionProgramImageOCRStatus,
)


PAGE_1 = b"\x89PNG\r\n\x1a\nsynthetic-page-1"
PAGE_2 = b"\xff\xd8\xffsynthetic-page-2"

PAGE_1_TEXT = """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data richiesta cliente: 2026-07-20
"""

PAGE_2_TEXT = """--- RECORD ---
ordine: ORD-002
codice: ART-002
qta: 8
scadenza: 2026-07-21
"""


@dataclass(frozen=True)
class PageOutcome:
    image_bytes: bytes
    result: OCRTextExtractionResult


class OrderedPageAdapter:
    def __init__(self, outcomes: tuple[PageOutcome, ...]) -> None:
        self._outcomes = {
            outcome.image_bytes: outcome.result
            for outcome in outcomes
        }
        self.calls: list[dict[str, object]] = []

    def extract_text(
        self,
        image_bytes: bytes,
        *,
        media_type: str,
        source_id: str,
    ) -> OCRTextExtractionResult:
        self.calls.append(
            {
                "image_bytes": image_bytes,
                "media_type": media_type,
                "source_id": source_id,
            }
        )
        return self._outcomes[image_bytes]


def _multipage_acquire():
    function = getattr(
        acquisition,
        "acquire_production_program_images_ocr",
        None,
    )
    assert callable(function), (
        "multipage acquisition contract missing: "
        "acquire_production_program_images_ocr"
    )
    return function


def test_multipage_acquisition_preserves_page_order_and_builds_one_preview() -> None:
    adapter = OrderedPageAdapter(
        (
            PageOutcome(
                PAGE_1,
                OCRTextExtractionResult(
                    ok=True,
                    provider="fake-local",
                    text=PAGE_1_TEXT,
                ),
            ),
            PageOutcome(
                PAGE_2,
                OCRTextExtractionResult(
                    ok=True,
                    provider="fake-local",
                    text=PAGE_2_TEXT,
                ),
            ),
        )
    )

    acquire_multipage = _multipage_acquire()
    result = acquire_multipage(
        (PAGE_1, PAGE_2),
        ocr_adapter=adapter,
    )

    assert result.ok is True
    assert result.status is ProductionProgramImageOCRStatus.PREVIEW_READY

    assert [call["image_bytes"] for call in adapter.calls] == [
        PAGE_1,
        PAGE_2,
    ]
    assert [call["media_type"] for call in adapter.calls] == [
        "image/png",
        "image/jpeg",
    ]

    assert result.page_count == 2
    assert len(result.page_source_ids) == 2
    assert result.page_source_ids[0].startswith(
        "production-program-image:sha256:"
    )
    assert result.page_source_ids[1].startswith(
        "production-program-image:sha256:"
    )

    assert result.source_id.startswith(
        "production-program-images:sha256:"
    )
    assert len(result.source_hash) == 64

    assert result.observed_text == PAGE_1_TEXT + PAGE_2_TEXT
    assert result.snapshot_preview is not None
    assert result.snapshot_preview["ok"] is True
    assert result.snapshot_preview["source_id"] == result.source_id
    assert len(result.snapshot_preview["orders"]) == 2

    assert result.snapshot_preview["persisted"] is False
    assert result.snapshot_preview["writer_called"] is False
    assert result.snapshot_preview["planner_called"] is False
    assert result.snapshot_preview["pattern_learning_called"] is False


def test_multipage_acquisition_fails_closed_when_one_page_ocr_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = OrderedPageAdapter(
        (
            PageOutcome(
                PAGE_1,
                OCRTextExtractionResult(
                    ok=True,
                    provider="fake-local",
                    text=PAGE_1_TEXT,
                ),
            ),
            PageOutcome(
                PAGE_2,
                OCRTextExtractionResult(
                    ok=False,
                    provider="fake-local",
                    error_code="SYNTHETIC_PAGE_OCR_FAILURE",
                ),
            ),
        )
    )

    def forbidden_preview(*args: object, **kwargs: object) -> object:
        raise AssertionError(
            "snapshot preview must not be built after a page OCR failure"
        )

    monkeypatch.setattr(
        acquisition,
        "build_production_program_snapshot_preview",
        forbidden_preview,
    )

    acquire_multipage = _multipage_acquire()
    result = acquire_multipage(
        (PAGE_1, PAGE_2),
        ocr_adapter=adapter,
    )

    assert result.ok is False
    assert result.status is ProductionProgramImageOCRStatus.OCR_FAILED
    assert result.error_code == "SYNTHETIC_PAGE_OCR_FAILURE"
    assert result.failed_page_number == 2
    assert result.snapshot_preview is None

    assert [call["image_bytes"] for call in adapter.calls] == [
        PAGE_1,
        PAGE_2,
    ]
