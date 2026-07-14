from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Protocol
import re

from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


ERROR_IMAGE_INPUT_REQUIRED = "IMAGE_INPUT_REQUIRED"
ERROR_INVALID_IMAGE_INPUT = "INVALID_IMAGE_INPUT"
ERROR_EMPTY_IMAGE = "EMPTY_IMAGE"
ERROR_UNSUPPORTED_IMAGE_FORMAT = "UNSUPPORTED_IMAGE_FORMAT"
ERROR_OCR_ADAPTER_REQUIRED = "OCR_ADAPTER_REQUIRED"
ERROR_OCR_EXTRACTION_FAILED = "OCR_EXTRACTION_FAILED"
ERROR_INVALID_OCR_RESULT = "INVALID_OCR_RESULT"
ERROR_OCR_EMPTY_TEXT = "OCR_EMPTY_TEXT"

SOURCE_ID_PREFIX = "production-program-image:sha256"


class ProductionProgramImageOCRStatus(str, Enum):
    REJECTED = "REJECTED"
    OCR_FAILED = "OCR_FAILED"
    PREVIEW_READY = "PREVIEW_READY"
    PREVIEW_BLOCKED = "PREVIEW_BLOCKED"


@dataclass(frozen=True)
class OCRTextExtractionResult:
    ok: bool
    provider: str = ""
    text: str = ""
    error_code: str | None = None


class ProductionProgramOCRAdapter(Protocol):
    def extract_text(
        self,
        image_bytes: bytes,
        *,
        media_type: str,
        source_id: str,
    ) -> OCRTextExtractionResult: ...


@dataclass(frozen=True)
class ProductionProgramImageOCRAcquisitionResult:
    ok: bool
    status: ProductionProgramImageOCRStatus
    source_id: str = ""
    source_hash: str = ""
    media_type: str | None = None
    provider: str = ""
    observed_text: str = ""
    normalized_lines: tuple[str, ...] = ()
    snapshot_preview: dict[str, object] | None = None
    error_code: str | None = None


def acquire_production_program_image_ocr(
    image_bytes: bytes | bytearray | memoryview | None,
    *,
    ocr_adapter: ProductionProgramOCRAdapter,
) -> ProductionProgramImageOCRAcquisitionResult:
    loaded_bytes, input_error = _coerce_image_bytes(image_bytes)
    if input_error is not None:
        return _rejected(input_error)
    assert loaded_bytes is not None

    media_type = _detect_media_type(loaded_bytes)
    if media_type is None:
        return _rejected(ERROR_UNSUPPORTED_IMAGE_FORMAT)

    source_hash = sha256(loaded_bytes).hexdigest()
    source_id = f"{SOURCE_ID_PREFIX}:{source_hash}"

    if not callable(getattr(ocr_adapter, "extract_text", None)):
        return _rejected(
            ERROR_OCR_ADAPTER_REQUIRED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    try:
        extraction = ocr_adapter.extract_text(
            loaded_bytes,
            media_type=media_type,
            source_id=source_id,
        )
    except Exception:
        return _ocr_failed(
            ERROR_OCR_EXTRACTION_FAILED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    if not isinstance(extraction, OCRTextExtractionResult):
        return _ocr_failed(
            ERROR_INVALID_OCR_RESULT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    if not extraction.ok:
        return _ocr_failed(
            extraction.error_code or ERROR_OCR_EXTRACTION_FAILED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
            provider=extraction.provider,
        )

    if not isinstance(extraction.text, str):
        return _ocr_failed(
            ERROR_INVALID_OCR_RESULT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
            provider=extraction.provider,
        )

    normalized_lines = _normalize_text_lines(extraction.text)
    if not normalized_lines:
        return _ocr_failed(
            ERROR_OCR_EMPTY_TEXT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
            provider=extraction.provider,
        )

    snapshot_preview = build_production_program_snapshot_preview(
        extraction.text,
        source_id=source_id,
    )
    preview_ok = snapshot_preview.get("ok") is True

    return ProductionProgramImageOCRAcquisitionResult(
        ok=preview_ok,
        status=(
            ProductionProgramImageOCRStatus.PREVIEW_READY
            if preview_ok
            else ProductionProgramImageOCRStatus.PREVIEW_BLOCKED
        ),
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        provider=extraction.provider,
        observed_text=extraction.text,
        normalized_lines=normalized_lines,
        snapshot_preview=snapshot_preview,
    )


def _coerce_image_bytes(
    value: bytes | bytearray | memoryview | None,
) -> tuple[bytes | None, str | None]:
    if value is None:
        return None, ERROR_IMAGE_INPUT_REQUIRED
    if not isinstance(value, (bytes, bytearray, memoryview)):
        return None, ERROR_INVALID_IMAGE_INPUT
    loaded = bytes(value)
    if not loaded:
        return None, ERROR_EMPTY_IMAGE
    return loaded, None


def _detect_media_type(image_bytes: bytes) -> str | None:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


def _normalize_text_lines(text: str) -> tuple[str, ...]:
    return tuple(
        normalized
        for line in text.splitlines()
        if (normalized := re.sub(r"\s+", " ", line).strip())
    )


def _rejected(
    error_code: str,
    *,
    source_id: str = "",
    source_hash: str = "",
    media_type: str | None = None,
) -> ProductionProgramImageOCRAcquisitionResult:
    return ProductionProgramImageOCRAcquisitionResult(
        ok=False,
        status=ProductionProgramImageOCRStatus.REJECTED,
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        error_code=error_code,
    )


def _ocr_failed(
    error_code: str,
    *,
    source_id: str,
    source_hash: str,
    media_type: str,
    provider: str = "",
) -> ProductionProgramImageOCRAcquisitionResult:
    return ProductionProgramImageOCRAcquisitionResult(
        ok=False,
        status=ProductionProgramImageOCRStatus.OCR_FAILED,
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        provider=provider,
        error_code=error_code,
    )
