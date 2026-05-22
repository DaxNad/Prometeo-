from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from app.services.controlled_import_audit import build_controlled_import_audit_dry_run
from app.services.controlled_import_persistent_audit import (
    ControlledImportPersistentAuditService,
)
from app.services.controlled_import_preview import build_controlled_import_preview


router = APIRouter(prefix="/controlled-import", tags=["controlled-import"])
PREVIEW_PAYLOAD_FIELDS = {
    "order_id",
    "article_code",
    "codice",
    "quantity",
    "qta",
    "due_date",
    "priority",
    "station",
    "postazione",
    "route",
    "note",
    "source_type",
}


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
    persist_audit: bool = False
    actor: str | None = None
    source: str | None = None
    confirmation_token_hash: str | None = None
    confirmation_token: str | None = None
    audit_event_id: str | None = None
    rollback_id: str | None = None


def get_persistent_audit_service() -> ControlledImportPersistentAuditService:
    return ControlledImportPersistentAuditService()


@router.post("/preview")
def controlled_import_preview(
    payload: ControlledImportPreviewRequest,
    persistent_audit_service: ControlledImportPersistentAuditService = Depends(
        get_persistent_audit_service
    ),
) -> dict[str, Any]:
    payload_data = payload.model_dump()
    preview = build_controlled_import_preview(_preview_payload(payload_data))
    audit_dry_run = build_controlled_import_audit_dry_run(preview)
    response = {
        **preview,
        "audit_dry_run": audit_dry_run,
        "audit_persistence": "NONE",
        "apply_allowed": False,
        "apply_executed": False,
    }

    if not payload.persist_audit:
        return response

    errors = _persistent_audit_binding_errors(payload, preview)
    if errors:
        return {
            **response,
            "persistent_audit": {
                "ok": False,
                "persistence_status": "BLOCKED",
                "error": "binding_validation_failed",
                "failure_reason": ";".join(errors),
                "apply_allowed": False,
                "apply_executed": False,
                "write_mode": "PREVIEW_ONLY",
            },
        }

    persistent_audit = persistent_audit_service.persist_preview_audit(
        preview_result=preview,
        audit_dry_run=audit_dry_run,
        actor=str(payload.actor),
        source=str(payload.source),
        confirmation_token_hash=str(payload.confirmation_token_hash),
        confirmation_token=payload.confirmation_token,
        audit_event_id=payload.audit_event_id,
        rollback_id=payload.rollback_id,
    )
    return {
        **response,
        "audit_persistence": persistent_audit.get("persistence_status", "FAILED"),
        "persistent_audit": persistent_audit,
        "apply_allowed": False,
        "apply_executed": False,
    }


def _preview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: payload.get(key) for key in PREVIEW_PAYLOAD_FIELDS if key in payload}


def _persistent_audit_binding_errors(
    payload: ControlledImportPreviewRequest,
    preview: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not str(payload.actor or "").strip():
        errors.append("actor_required")
    if not str(payload.source or "").strip():
        errors.append("source_required")
    if not str(payload.confirmation_token_hash or "").strip():
        errors.append("confirmation_token_hash_required")
    if payload.confirmation_token is not None:
        errors.append("clear_confirmation_token_forbidden")
    if str(preview.get("risk_level") or "").upper() == "BLOCKED":
        errors.append("blocked_risk_not_persisted_for_preview")
    return errors
