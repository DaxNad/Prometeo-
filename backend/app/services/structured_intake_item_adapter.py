from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.intake_destination_classifier import IntakeItem


ERROR_INVALID_PAYLOAD = "INVALID_PAYLOAD"
ERROR_MISSING_FIELD_NAME = "MISSING_FIELD_NAME"
ERROR_MISSING_SOURCE_ID = "MISSING_SOURCE_ID"


_ALLOWED_FIELDS = frozenset(
    {
        "field_name",
        "value",
        "source_id",
        "source_type",
        "source_status",
        "semantic_status",
        "authority_role",
        "document_section",
        "document_label",
        "context",
        "metadata",
    }
)


class StructuredIntakeAdapterStatus(str, Enum):
    BUILT = "BUILT"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class StructuredIntakeAdapterResult:
    ok: bool
    status: StructuredIntakeAdapterStatus
    item: IntakeItem | None
    error_code: str | None = None


def build_intake_item(payload: Mapping[str, Any]) -> StructuredIntakeAdapterResult:
    if not isinstance(payload, Mapping):
        return _rejected(ERROR_INVALID_PAYLOAD)

    if not set(payload).issubset(_ALLOWED_FIELDS):
        return _rejected(ERROR_INVALID_PAYLOAD)

    field_name = _clean(payload.get("field_name"))
    if not field_name:
        return _rejected(ERROR_MISSING_FIELD_NAME)

    source_id = _clean(payload.get("source_id"))
    if not source_id:
        return _rejected(ERROR_MISSING_SOURCE_ID)

    context = payload.get("context")
    metadata = payload.get("metadata")

    if context is not None and not isinstance(context, Mapping):
        return _rejected(ERROR_INVALID_PAYLOAD)

    if metadata is not None and not isinstance(metadata, Mapping):
        return _rejected(ERROR_INVALID_PAYLOAD)

    item = IntakeItem(
        field_name=field_name,
        value=deepcopy(payload.get("value")),
        source_id=source_id,
        source_type=_optional_text(payload.get("source_type")),
        source_status=_optional_text(payload.get("source_status")),
        semantic_status=_optional_text(payload.get("semantic_status")),
        authority_role=_optional_text(payload.get("authority_role")),
        document_section=_optional_text(payload.get("document_section")),
        document_label=_optional_text(payload.get("document_label")),
        context=deepcopy(dict(context)) if context is not None else None,
        metadata=deepcopy(dict(metadata)) if metadata is not None else None,
    )

    return StructuredIntakeAdapterResult(
        ok=True,
        status=StructuredIntakeAdapterStatus.BUILT,
        item=item,
    )


def _rejected(error_code: str) -> StructuredIntakeAdapterResult:
    return StructuredIntakeAdapterResult(
        ok=False,
        status=StructuredIntakeAdapterStatus.REJECTED,
        item=None,
        error_code=error_code,
    )


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _optional_text(value: Any) -> str | None:
    cleaned = _clean(value)
    return cleaned or None
