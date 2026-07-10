from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Protocol
import re

from app.ingest.article_specification_parser import (
    ArticleSpecificationParseResult,
    parse_article_specification_rows,
)


ERROR_IMAGE_INPUT_REQUIRED = "IMAGE_INPUT_REQUIRED"
ERROR_MULTIPLE_IMAGE_INPUTS = "MULTIPLE_IMAGE_INPUTS"
ERROR_INVALID_IMAGE_INPUT = "INVALID_IMAGE_INPUT"
ERROR_IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
ERROR_IMAGE_READ_FAILED = "IMAGE_READ_FAILED"
ERROR_EMPTY_IMAGE = "EMPTY_IMAGE"
ERROR_UNSUPPORTED_IMAGE_FORMAT = "UNSUPPORTED_IMAGE_FORMAT"
ERROR_OCR_ADAPTER_REQUIRED = "OCR_ADAPTER_REQUIRED"
ERROR_INVALID_OCR_RESULT = "INVALID_OCR_RESULT"
ERROR_OCR_EXTRACTION_FAILED = "OCR_EXTRACTION_FAILED"
ERROR_OCR_EMPTY_TEXT = "OCR_EMPTY_TEXT"
ERROR_PARSER_REJECTED = "ARTICLE_SPECIFICATION_PARSER_REJECTED"

SOURCE_ID_PREFIX = "article-spec-image:sha256"


class ImageAcquisitionStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    REJECTED = "REJECTED"
    OCR_FAILED = "OCR_FAILED"
    PARSER_REJECTED = "PARSER_REJECTED"


@dataclass(frozen=True)
class OCRTextExtractionResult:
    ok: bool
    text: str = ""
    error_code: str | None = None


class ArticleSpecificationOCRAdapter(Protocol):
    def extract_text(
        self,
        image_bytes: bytes,
        *,
        media_type: str,
        source_id: str,
    ) -> OCRTextExtractionResult: ...


@dataclass(frozen=True)
class ArticleSpecificationImageAcquisitionResult:
    ok: bool
    status: ImageAcquisitionStatus
    source_id: str = ""
    source_hash: str = ""
    media_type: str | None = None
    extracted_text: str = ""
    normalized_lines: tuple[str, ...] = ()
    parser_result: ArticleSpecificationParseResult | None = None
    error_code: str | None = None


def acquire_article_specification_image(
    *,
    ocr_adapter: ArticleSpecificationOCRAdapter,
    image_path: str | Path | None = None,
    image_bytes: bytes | bytearray | memoryview | None = None,
) -> ArticleSpecificationImageAcquisitionResult:
    input_error = _validate_input_choice(
        image_path=image_path,
        image_bytes=image_bytes,
    )
    if input_error is not None:
        return _rejected(input_error)

    loaded_bytes, load_error = _load_image_bytes(
        image_path=image_path,
        image_bytes=image_bytes,
    )
    if load_error is not None:
        return _rejected(load_error)
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
            error_code=ERROR_OCR_EXTRACTION_FAILED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    if not isinstance(extraction, OCRTextExtractionResult):
        return _ocr_failed(
            error_code=ERROR_INVALID_OCR_RESULT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    if not extraction.ok:
        return _ocr_failed(
            error_code=extraction.error_code or ERROR_OCR_EXTRACTION_FAILED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    if not isinstance(extraction.text, str):
        return _ocr_failed(
            error_code=ERROR_INVALID_OCR_RESULT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    normalized_lines = _normalize_text_lines(extraction.text)
    if not normalized_lines:
        return _ocr_failed(
            error_code=ERROR_OCR_EMPTY_TEXT,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
        )

    parser_result = parse_article_specification_rows(
        normalized_lines,
        source_id=source_id,
    )
    if not parser_result.ok:
        return ArticleSpecificationImageAcquisitionResult(
            ok=False,
            status=ImageAcquisitionStatus.PARSER_REJECTED,
            source_id=source_id,
            source_hash=source_hash,
            media_type=media_type,
            extracted_text=extraction.text,
            normalized_lines=normalized_lines,
            parser_result=parser_result,
            error_code=ERROR_PARSER_REJECTED,
        )

    return ArticleSpecificationImageAcquisitionResult(
        ok=True,
        status=ImageAcquisitionStatus.EXTRACTED,
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        extracted_text=extraction.text,
        normalized_lines=normalized_lines,
        parser_result=parser_result,
    )


def _validate_input_choice(
    *,
    image_path: str | Path | None,
    image_bytes: bytes | bytearray | memoryview | None,
) -> str | None:
    if image_path is None and image_bytes is None:
        return ERROR_IMAGE_INPUT_REQUIRED
    if image_path is not None and image_bytes is not None:
        return ERROR_MULTIPLE_IMAGE_INPUTS
    return None


def _load_image_bytes(
    *,
    image_path: str | Path | None,
    image_bytes: bytes | bytearray | memoryview | None,
) -> tuple[bytes | None, str | None]:
    if image_bytes is not None:
        if not isinstance(image_bytes, (bytes, bytearray, memoryview)):
            return None, ERROR_INVALID_IMAGE_INPUT
        loaded_bytes = bytes(image_bytes)
    else:
        if not isinstance(image_path, (str, Path)) or not str(image_path).strip():
            return None, ERROR_INVALID_IMAGE_INPUT
        path = Path(image_path)
        if not path.is_file():
            return None, ERROR_IMAGE_NOT_FOUND
        try:
            loaded_bytes = path.read_bytes()
        except OSError:
            return None, ERROR_IMAGE_READ_FAILED

    if not loaded_bytes:
        return None, ERROR_EMPTY_IMAGE
    return loaded_bytes, None


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
) -> ArticleSpecificationImageAcquisitionResult:
    return ArticleSpecificationImageAcquisitionResult(
        ok=False,
        status=ImageAcquisitionStatus.REJECTED,
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        error_code=error_code,
    )


def _ocr_failed(
    *,
    error_code: str,
    source_id: str,
    source_hash: str,
    media_type: str,
) -> ArticleSpecificationImageAcquisitionResult:
    return ArticleSpecificationImageAcquisitionResult(
        ok=False,
        status=ImageAcquisitionStatus.OCR_FAILED,
        source_id=source_id,
        source_hash=source_hash,
        media_type=media_type,
        error_code=error_code,
    )
