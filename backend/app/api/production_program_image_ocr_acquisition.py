from __future__ import annotations

import base64
import binascii
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.ingest.production_program_image_ocr_acquisition import (
    ProductionProgramOCRAdapter,
    acquire_production_program_image_ocr,
    acquire_production_program_images_ocr,
)
from app.services.production_program_tesseract_ocr import (
    build_production_program_ocr_adapter,
)


router = APIRouter(
    prefix="/production-program/image-ocr",
    tags=["production-program-image-ocr"],
)


class ProductionProgramImageOCRAcquisitionRequest(BaseModel):
    image_base64: str = Field(min_length=1)


class ProductionProgramImagesOCRAcquisitionRequest(BaseModel):
    images_base64: list[str] = Field(min_length=1)


def get_production_program_ocr_adapter() -> ProductionProgramOCRAdapter | None:
    """Resolve the explicitly configured local OCR provider.

    The default remains fail-closed: without an enabled and available provider,
    acquisition returns OCR_ADAPTER_REQUIRED.
    """
    return build_production_program_ocr_adapter()


@router.post("/acquire")
def acquire_production_program_image_ocr_endpoint(
    payload: ProductionProgramImageOCRAcquisitionRequest,
    ocr_adapter: ProductionProgramOCRAdapter | None = Depends(
        get_production_program_ocr_adapter
    ),
) -> dict[str, Any]:
    try:
        image_bytes = base64.b64decode(payload.image_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail="INVALID_IMAGE_BASE64",
        ) from exc

    acquisition = acquire_production_program_image_ocr(
        image_bytes=image_bytes,
        ocr_adapter=ocr_adapter,  # type: ignore[arg-type]
    )

    return {
        "ok": acquisition.ok,
        "status": acquisition.status.value,
        "source_id": acquisition.source_id,
        "source_hash": acquisition.source_hash,
        "media_type": acquisition.media_type,
        "provider": acquisition.provider,
        "error_code": acquisition.error_code,
        "requires_confirmation": True,
        "semantic_status": "DA_VERIFICARE",
        "persisted": False,
        "writer_called": False,
        "planner_called": False,
        "pattern_learning_called": False,
        "observed_text": acquisition.observed_text,
        "normalized_lines": list(acquisition.normalized_lines),
        "snapshot_preview": acquisition.snapshot_preview,
    }

@router.post("/acquire-multipage")
def acquire_production_program_images_ocr_endpoint(
    payload: ProductionProgramImagesOCRAcquisitionRequest,
    ocr_adapter: ProductionProgramOCRAdapter | None = Depends(
        get_production_program_ocr_adapter
    ),
) -> dict[str, Any]:
    decoded_images: list[bytes] = []

    for image_base64 in payload.images_base64:
        try:
            image_bytes = base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail="INVALID_IMAGE_BASE64",
            ) from exc

        decoded_images.append(image_bytes)

    acquisition = acquire_production_program_images_ocr(
        images=tuple(decoded_images),
        ocr_adapter=ocr_adapter,  # type: ignore[arg-type]
    )

    return {
        "ok": acquisition.ok,
        "status": acquisition.status.value,
        "source_id": acquisition.source_id,
        "source_hash": acquisition.source_hash,
        "media_type": acquisition.media_type,
        "provider": acquisition.provider,
        "error_code": acquisition.error_code,
        "page_count": acquisition.page_count,
        "page_source_ids": list(acquisition.page_source_ids),
        "failed_page_number": acquisition.failed_page_number,
        "requires_confirmation": True,
        "semantic_status": "DA_VERIFICARE",
        "persisted": False,
        "writer_called": False,
        "planner_called": False,
        "pattern_learning_called": False,
        "observed_text": acquisition.observed_text,
        "normalized_lines": list(acquisition.normalized_lines),
        "snapshot_preview": acquisition.snapshot_preview,
    }
