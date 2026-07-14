from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


router = APIRouter(
    prefix="/production-program-snapshot",
    tags=["production-program-snapshot"],
)


class ProductionProgramSnapshotPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    structured_text: str
    source_id: str | None = None


@router.post("/preview")
def production_program_snapshot_preview(
    payload: ProductionProgramSnapshotPreviewRequest,
) -> dict[str, Any]:
    return build_production_program_snapshot_preview(
        payload.structured_text,
        source_id=payload.source_id,
    )
