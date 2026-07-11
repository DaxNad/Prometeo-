from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.structured_intake_orchestration_facade import (
    process_structured_intake_payload,
)


router = APIRouter(
    prefix="/article-specification",
    tags=["article-specification"],
)


class ArticleSpecificationConfirmationRequest(BaseModel):
    article: str = Field(min_length=1)
    operational_class: str = Field(min_length=1)
    planner_eligible: bool
    tl_confirmation_required: bool
    authority_role: str = Field(min_length=1)
    audit_note: str = Field(min_length=1)
    source_id: str | None = None
    confirmed_at: str | None = None
    material: str | None = None
    drawing: str | None = None
    description: str | None = None


@router.post("/confirm")
def confirm_article_specification_endpoint(
    payload: ArticleSpecificationConfirmationRequest,
) -> dict[str, Any]:
    article = payload.article.strip()
    authority_role = payload.authority_role.strip()
    source_id = (
        payload.source_id.strip()
        if payload.source_id is not None and payload.source_id.strip()
        else f"human:article-specification:{article}"
    )

    metadata: dict[str, Any] = {
        "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
        "audit_note": payload.audit_note.strip(),
    }
    for key, value in (
        ("confirmed_at", payload.confirmed_at),
        ("material", payload.material),
        ("drawing", payload.drawing),
        ("description", payload.description),
    ):
        if value is not None and value.strip():
            metadata[key] = value.strip()

    result = process_structured_intake_payload(
        {
            "field_name": "operational_class",
            "value": payload.operational_class.strip(),
            "source_id": source_id,
            "source_type": "human_operational_confirmation",
            "source_status": "SOURCE_FOUND",
            "semantic_status": "CERTO",
            "authority_role": authority_role,
            "context": {
                "article": article,
                "planner_eligible": payload.planner_eligible,
                "tl_confirmation_required": payload.tl_confirmation_required,
            },
            "metadata": metadata,
        },
        requested_by_role=authority_role,
    )

    orchestration = result.orchestration_result
    execution = orchestration.execution if orchestration is not None else None

    return {
        "ok": result.ok,
        "status": result.status.value,
        "source_id": result.source_id or source_id,
        "writer_called": result.writer_called,
        "persisted": execution.persisted if execution is not None else False,
        "created": execution.created if execution is not None else False,
        "updated": execution.updated if execution is not None else False,
        "error_code": result.error_code,
    }
