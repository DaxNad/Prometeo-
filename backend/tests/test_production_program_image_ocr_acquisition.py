from __future__ import annotations

from dataclasses import FrozenInstanceError
from hashlib import sha256

import pytest

import app.ingest.production_program_image_ocr_acquisition as acquisition
from app.ingest.production_program_image_ocr_acquisition import (
    ERROR_EMPTY_IMAGE,
    ERROR_IMAGE_INPUT_REQUIRED,
    ERROR_INVALID_IMAGE_INPUT,
    ERROR_INVALID_OCR_RESULT,
    ERROR_OCR_ADAPTER_REQUIRED,
    ERROR_OCR_EMPTY_TEXT,
    ERROR_OCR_EXTRACTION_FAILED,
    ERROR_UNSUPPORTED_IMAGE_FORMAT,
    OCRTextExtractionResult,
    ProductionProgramImageOCRStatus,
    acquire_production_program_image_ocr,
)
from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


PNG = b"\x89PNG\r\n\x1a\nsynthetic-png"
JPEG = b"\xff\xd8\xffsynthetic-jpeg"
VALID_TEXT = """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data richiesta cliente: 2026-07-20
--- RECORD ---
ordine: ORD-002
codice: ART-002
qta: 8
scadenza: 2026-07-21
"""


class FakeAdapter:
    def __init__(
        self,
        result: OCRTextExtractionResult | object,
        *,
        raises: bool = False,
    ) -> None:
        self.result = result
        self.raises = raises
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
        if self.raises:
            raise RuntimeError("synthetic failure")
        return self.result  # type: ignore[return-value]


def _successful_adapter(text: str = VALID_TEXT) -> FakeAdapter:
    return FakeAdapter(
        OCRTextExtractionResult(ok=True, provider="fake-local", text=text)
    )


@pytest.mark.parametrize(
    ("image_bytes", "expected_media_type"),
    [(PNG, "image/png"), (JPEG, "image/jpeg")],
)
def test_valid_png_and_jpeg_pass_detected_media_to_adapter(
    image_bytes: bytes,
    expected_media_type: str,
) -> None:
    adapter = _successful_adapter()

    result = acquire_production_program_image_ocr(
        image_bytes,
        ocr_adapter=adapter,
    )

    assert result.ok is True
    assert result.status is ProductionProgramImageOCRStatus.PREVIEW_READY
    assert result.media_type == expected_media_type
    assert adapter.calls == [
        {
            "image_bytes": image_bytes,
            "media_type": expected_media_type,
            "source_id": result.source_id,
        }
    ]


def test_identity_is_deterministic_domain_specific_and_changes_with_bytes() -> None:
    first = acquire_production_program_image_ocr(PNG, ocr_adapter=_successful_adapter())
    repeated = acquire_production_program_image_ocr(PNG, ocr_adapter=_successful_adapter())
    different = acquire_production_program_image_ocr(
        PNG + b"-different",
        ocr_adapter=_successful_adapter(),
    )

    expected_hash = sha256(PNG).hexdigest()
    assert first.source_hash == expected_hash
    assert first.source_id == f"production-program-image:sha256:{expected_hash}"
    assert repeated.source_id == first.source_id
    assert different.source_id != first.source_id
    assert "article-spec-image" not in first.source_id


def test_exact_text_and_whitespace_only_lines_are_preserved() -> None:
    text = "  PERIODO: 2026-W29  \n\nordine:   ORD-001\n  codice: ART-001  \nqta: 4\n--- RECORD ---\nordine: ORD-002\ncodice: ART-002\nqta: 2\n"

    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=_successful_adapter(text),
    )

    assert result.observed_text == text
    assert result.normalized_lines == (
        "PERIODO: 2026-W29",
        "ordine: ORD-001",
        "codice: ART-001",
        "qta: 4",
        "--- RECORD ---",
        "ordine: ORD-002",
        "codice: ART-002",
        "qta: 2",
    )


def test_snapshot_preview_equals_direct_service_output_unchanged() -> None:
    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=_successful_adapter(),
    )
    expected = build_production_program_snapshot_preview(
        VALID_TEXT,
        source_id=result.source_id,
    )

    assert result.snapshot_preview == expected
    assert result.snapshot_preview is not None
    assert result.snapshot_preview["source_id"] == result.source_id
    assert result.snapshot_preview["requires_confirmation"] is True
    assert result.snapshot_preview["persisted"] is False
    assert result.snapshot_preview["writer_called"] is False
    assert result.snapshot_preview["planner_called"] is False
    assert result.snapshot_preview["pattern_learning_called"] is False


def test_missing_delimiter_remains_downstream_blocked() -> None:
    text = "PERIODO: 2026-W29\nordine: ORD-001\ncodice: ART-001\nqta: 12"

    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=_successful_adapter(text),
    )

    assert result.ok is False
    assert result.status is ProductionProgramImageOCRStatus.PREVIEW_BLOCKED
    assert result.snapshot_preview is not None
    assert result.snapshot_preview["ok"] is False
    assert result.snapshot_preview["semantic_status"] == "BLOCCATO"
    assert result.snapshot_preview["discrepancies"] == ["record_delimiter_required"]


def test_generic_date_remains_ambiguous() -> None:
    text = """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data: 2026-07-20
--- RECORD ---
ordine: ORD-002
codice: ART-002
qta: 8
"""

    result = acquire_production_program_image_ocr(
        JPEG,
        ocr_adapter=_successful_adapter(text),
    )

    assert result.snapshot_preview is not None
    assert result.snapshot_preview["ambiguous_fields"] == [
        {
            "record_index": 1,
            "field": "date_meaning",
            "raw_value": "2026-07-20",
            "source_line": "data: 2026-07-20",
            "observed_label": "data",
        }
    ]
    first_order = result.snapshot_preview["orders"][0]
    assert first_order["customer_requested_date"] is None


@pytest.mark.parametrize(
    ("image_bytes", "error_code"),
    [
        (None, ERROR_IMAGE_INPUT_REQUIRED),
        ("not-bytes", ERROR_INVALID_IMAGE_INPUT),
        (b"", ERROR_EMPTY_IMAGE),
        (b"GIF89a", ERROR_UNSUPPORTED_IMAGE_FORMAT),
    ],
)
def test_invalid_inputs_fail_closed_without_calling_adapter(
    image_bytes: object,
    error_code: str,
) -> None:
    adapter = _successful_adapter()

    result = acquire_production_program_image_ocr(
        image_bytes,  # type: ignore[arg-type]
        ocr_adapter=adapter,
    )

    assert result.ok is False
    assert result.status is ProductionProgramImageOCRStatus.REJECTED
    assert result.error_code == error_code
    assert result.snapshot_preview is None
    assert adapter.calls == []


def test_missing_adapter_fails_closed() -> None:
    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=object(),  # type: ignore[arg-type]
    )

    assert result.ok is False
    assert result.status is ProductionProgramImageOCRStatus.REJECTED
    assert result.error_code == ERROR_OCR_ADAPTER_REQUIRED
    assert result.snapshot_preview is None


@pytest.mark.parametrize(
    ("adapter", "error_code"),
    [
        (FakeAdapter(object()), ERROR_INVALID_OCR_RESULT),
        (FakeAdapter(OCRTextExtractionResult(ok=True, provider="fake", text="   \n")), ERROR_OCR_EMPTY_TEXT),
        (FakeAdapter(OCRTextExtractionResult(ok=True, provider="fake", text=123)), ERROR_INVALID_OCR_RESULT),
        (FakeAdapter(OCRTextExtractionResult(ok=False, provider="fake")), ERROR_OCR_EXTRACTION_FAILED),
        (FakeAdapter(OCRTextExtractionResult(ok=True), raises=True), ERROR_OCR_EXTRACTION_FAILED),
    ],
)
def test_invalid_adapter_outcomes_fail_closed(
    adapter: FakeAdapter,
    error_code: str,
) -> None:
    result = acquire_production_program_image_ocr(PNG, ocr_adapter=adapter)

    assert result.ok is False
    assert result.status is ProductionProgramImageOCRStatus.OCR_FAILED
    assert result.error_code == error_code
    assert result.snapshot_preview is None
    assert len(adapter.calls) == 1


def test_adapter_error_code_is_preserved() -> None:
    adapter = FakeAdapter(
        OCRTextExtractionResult(
            ok=False,
            provider="fake-local",
            error_code="SYNTHETIC_OCR_TIMEOUT",
        )
    )

    result = acquire_production_program_image_ocr(PNG, ocr_adapter=adapter)

    assert result.error_code == "SYNTHETIC_OCR_TIMEOUT"
    assert result.provider == "fake-local"


def test_snapshot_service_called_once_only_after_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    sentinel = {
        "ok": True,
        "requires_confirmation": True,
        "persisted": False,
        "writer_called": False,
        "planner_called": False,
        "pattern_learning_called": False,
    }

    def fake_builder(text: str, *, source_id: str) -> dict[str, object]:
        calls.append((text, source_id))
        return sentinel

    monkeypatch.setattr(acquisition, "build_production_program_snapshot_preview", fake_builder)

    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=_successful_adapter(),
    )

    assert calls == [(VALID_TEXT, result.source_id)]
    assert result.snapshot_preview is sentinel


@pytest.mark.parametrize(
    "adapter",
    [
        FakeAdapter(OCRTextExtractionResult(ok=False, error_code="OCR_FAILED")),
        FakeAdapter(object()),
        FakeAdapter(OCRTextExtractionResult(ok=True, text="")),
    ],
)
def test_snapshot_service_not_called_after_acquisition_failure(
    adapter: FakeAdapter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_builder(*args: object, **kwargs: object) -> dict[str, object]:
        raise AssertionError("snapshot service must not be called")

    monkeypatch.setattr(acquisition, "build_production_program_snapshot_preview", forbidden_builder)

    result = acquire_production_program_image_ocr(PNG, ocr_adapter=adapter)

    assert result.ok is False
    assert result.snapshot_preview is None


def test_runtime_uses_no_forbidden_side_effect_components(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("forbidden side effect invoked")

    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr("subprocess.run", forbidden)
    monkeypatch.setattr("socket.create_connection", forbidden)

    result = acquire_production_program_image_ocr(
        PNG,
        ocr_adapter=_successful_adapter(),
    )

    assert result.ok is True
    assert result.snapshot_preview is not None
    assert result.snapshot_preview["persisted"] is False
    assert result.snapshot_preview["writer_called"] is False
    assert result.snapshot_preview["planner_called"] is False
    assert result.snapshot_preview["pattern_learning_called"] is False


def test_result_structures_are_immutable() -> None:
    extraction = OCRTextExtractionResult(ok=True, provider="fake", text=VALID_TEXT)
    result = acquire_production_program_image_ocr(PNG, ocr_adapter=FakeAdapter(extraction))

    with pytest.raises(FrozenInstanceError):
        extraction.text = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.ok = False  # type: ignore[misc]
