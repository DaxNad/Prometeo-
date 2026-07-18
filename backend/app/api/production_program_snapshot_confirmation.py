from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from app.domain.production_program_snapshot_registry import (
    ProductionProgramSnapshotRegistry,
    get_production_program_snapshot_registry,
)
from app.services.production_program_snapshot_confirmation import (
    confirm_production_program_snapshot,
)


router = APIRouter(
    prefix="/production-program-snapshot",
    tags=["production-program-snapshot"],
)


class ProductionProgramSnapshotConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    source_hash: str = Field(min_length=1)
    observed_text: str = Field(min_length=1)
    snapshot_preview: dict[str, Any]
    actor_id: str = Field(min_length=1)
    authority_role: str = Field(min_length=1)
    confirmed_at: str = Field(min_length=1)
    audit_note: str = Field(min_length=1)


@router.post("/confirm")
def confirm_production_program_snapshot_endpoint(
    payload: ProductionProgramSnapshotConfirmationRequest,
    registry: ProductionProgramSnapshotRegistry | None = Depends(
        get_production_program_snapshot_registry
    ),
) -> dict[str, Any]:
    return confirm_production_program_snapshot(
        registry=registry,
        source_id=payload.source_id,
        source_hash=payload.source_hash,
        observed_text=payload.observed_text,
        snapshot_preview=payload.snapshot_preview,
        actor_id=payload.actor_id,
        authority_role=payload.authority_role,
        confirmed_at=payload.confirmed_at,
        audit_note=payload.audit_note,
    ).as_dict()
