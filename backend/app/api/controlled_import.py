from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from app.services.controlled_import_audit import build_controlled_import_audit_dry_run
from app.services.controlled_import_preview import build_controlled_import_preview


router = APIRouter(prefix="/controlled-import", tags=["controlled-import"])


class ControlledImportPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    order_id: str | None = None
    article_code: str | None = None
    codice: str | None = None
    quantity: int | float | str | None = None
    qta: int | float | str | None = None
    due_date: str | None = None
    priority: str | None = None
    station: str | None = None
    postazione: str | None = None
    route: list[str] | None = None
    note: str | None = None
    source_type: str | None = None


@router.post("/preview")
def controlled_import_preview(payload: ControlledImportPreviewRequest) -> dict[str, Any]:
    preview = build_controlled_import_preview(payload.model_dump())
    audit_dry_run = build_controlled_import_audit_dry_run(preview)
    return {
        **preview,
        "audit_dry_run": audit_dry_run,
        "audit_persistence": "NONE",
        "apply_allowed": False,
    }
