from __future__ import annotations

import base64
import binascii
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.ingest.article_specification_image_acquisition import (
    ArticleSpecificationOCRAdapter,
    acquire_article_specification_image,
)
from app.services.article_specification_intake_binding import (
    bind_article_specification_acquisition,
)
from app.services.article_specification_tesseract_ocr import (
    build_article_specification_ocr_adapter,
)


router = APIRouter(
    prefix="/article-specification",
    tags=["article-specification"],
)


class ArticleSpecificationAcquisitionRequest(BaseModel):
    image_base64: str = Field(min_length=1)


def get_article_specification_ocr_adapter() -> ArticleSpecificationOCRAdapter | None:
    """Resolve the explicitly configured local OCR provider.

    The default remains fail-closed: without an enabled and available provider,
    acquisition returns OCR_ADAPTER_REQUIRED.
    """
    return build_article_specification_ocr_adapter()


@router.post("/acquire")
def acquire_article_specification_endpoint(
    payload: ArticleSpecificationAcquisitionRequest,
    ocr_adapter: ArticleSpecificationOCRAdapter | None = Depends(
        get_article_specification_ocr_adapter
    ),
) -> dict[str, Any]:
    try:
        image_bytes = base64.b64decode(payload.image_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail="INVALID_IMAGE_BASE64",
        ) from exc

    acquisition = acquire_article_specification_image(
        image_bytes=image_bytes,
        ocr_adapter=ocr_adapter,  # type: ignore[arg-type]
    )
    binding = bind_article_specification_acquisition(acquisition)

    parser_result = acquisition.parser_result
    review_payloads = (
        [dict(item) for item in parser_result.payloads]
        if parser_result is not None
        else []
    )

    facade_results = [
        {
            "ok": result.ok,
            "status": result.status.value,
            "writer_called": result.writer_called,
            "source_id": result.source_id,
            "error_code": result.error_code,
        }
        for result in binding.facade_results
    ]

    return {
        "ok": acquisition.ok and binding.ok,
        "status": binding.status.value,
        "source_id": binding.source_id,
        "semantic_status": binding.semantic_status,
        "writer_called": binding.writer_called,
        "persisted": binding.persisted,
        "requires_review": binding.requires_review,
        "error_code": binding.error_code,
        "acquisition": {
            "ok": acquisition.ok,
            "status": acquisition.status.value,
            "source_id": acquisition.source_id,
            "source_hash": acquisition.source_hash,
            "media_type": acquisition.media_type,
            "error_code": acquisition.error_code,
        },
        "review_payloads": review_payloads,
        "facade_results": facade_results,
    }
