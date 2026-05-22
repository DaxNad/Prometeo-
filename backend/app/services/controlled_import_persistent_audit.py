from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.repositories.controlled_import_audit_repository import (
    ControlledImportAuditRepository,
)


CAPABILITY = "CONTROLLED_IMPORT_PERSISTENT_AUDIT_SERVICE_V1"
DEFAULT_AUDIT_EVENT_TYPE = "CONTROLLED_IMPORT_PREVIEW_EVALUATED"
DEFAULT_SOURCE = "controlled-import-persistent-audit-service"
BLOCKED_RISK_LEVEL = "BLOCKED"


class ControlledImportPersistentAuditService:
    def __init__(
        self,
        repository: Any | None = None,
        id_factory: Callable[[], str] | None = None,
        rollback_id_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository or ControlledImportAuditRepository()
        self._id_factory = id_factory or _default_audit_event_id
        self._rollback_id_factory = rollback_id_factory or _default_rollback_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def persist_preview_audit(
        self,
        *,
        preview_result: dict[str, Any],
        audit_dry_run: dict[str, Any],
        actor: str,
        source: str = DEFAULT_SOURCE,
        confirmation_token_hash: str | None = None,
        confirmation_token: str | None = None,
        audit_event_id: str | None = None,
        rollback_id: str | None = None,
    ) -> dict[str, Any]:
        errors = self._validate_request(
            preview_result=preview_result,
            audit_dry_run=audit_dry_run,
            actor=actor,
            source=source,
            confirmation_token_hash=confirmation_token_hash,
            confirmation_token=confirmation_token,
        )
        if errors:
            return _blocked_result(
                audit_event_id=audit_event_id,
                errors=errors,
                rollback_id=rollback_id,
            )

        preview_copy = deepcopy(preview_result)
        dry_run_copy = deepcopy(audit_dry_run)
        record = self._build_record(
            preview_result=preview_copy,
            audit_dry_run=dry_run_copy,
            actor=actor,
            source=source,
            confirmation_token_hash=str(confirmation_token_hash),
            audit_event_id=audit_event_id or self._id_factory(),
            rollback_id=rollback_id or self._rollback_id_factory(),
        )
        repository_result = self._repository.record_event(record)

        return {
            "ok": bool(repository_result.get("ok")),
            "capability": CAPABILITY,
            "audit_event_id": record["audit_event_id"],
            "rollback_id": record["rollback_id"],
            "write_mode": "PREVIEW_ONLY",
            "apply_allowed": False,
            "apply_executed": False,
            "persistence_status": str(
                repository_result.get("persistence_status")
                or record["persistence_status"]
            ),
            "repository_result": repository_result,
            "record": record,
            "error": repository_result.get("error"),
            "failure_reason": repository_result.get("failure_reason"),
        }

    def _validate_request(
        self,
        *,
        preview_result: dict[str, Any],
        audit_dry_run: dict[str, Any],
        actor: str,
        source: str,
        confirmation_token_hash: str | None,
        confirmation_token: str | None,
    ) -> list[str]:
        errors: list[str] = []
        if not isinstance(preview_result, dict):
            errors.append("preview_result_must_be_object")
        if not isinstance(audit_dry_run, dict):
            errors.append("audit_dry_run_must_be_object")
        if not str(actor or "").strip():
            errors.append("actor_required")
        if not str(source or "").strip():
            errors.append("source_required")
        if confirmation_token is not None:
            errors.append("clear_confirmation_token_forbidden")
        if not str(confirmation_token_hash or "").strip():
            errors.append("confirmation_token_hash_required")
        if isinstance(preview_result, dict) and "confirmation_token" in preview_result:
            errors.append("preview_clear_confirmation_token_forbidden")
        if isinstance(audit_dry_run, dict) and "confirmation_token" in audit_dry_run:
            errors.append("dry_run_clear_confirmation_token_forbidden")
        if _risk_level(preview_result, audit_dry_run) == BLOCKED_RISK_LEVEL:
            errors.append("blocked_risk_not_persisted_for_preview")
        return errors

    def _build_record(
        self,
        *,
        preview_result: dict[str, Any],
        audit_dry_run: dict[str, Any],
        actor: str,
        source: str,
        confirmation_token_hash: str,
        audit_event_id: str,
        rollback_id: str,
    ) -> dict[str, Any]:
        timestamp = str(audit_dry_run.get("timestamp_utc") or self._now_iso())
        risk_level = _risk_level(preview_result, audit_dry_run)
        return {
            "audit_event_id": audit_event_id,
            "audit_event_type": str(
                audit_dry_run.get("audit_event_type") or DEFAULT_AUDIT_EVENT_TYPE
            ),
            "actor": str(actor).strip(),
            "source": str(source).strip(),
            "timestamp_utc": timestamp,
            "preview_reference": _stable_reference("preview", preview_result),
            "dry_run_reference": _stable_reference("dry-run", audit_dry_run),
            "confirmation_token_hash": confirmation_token_hash.strip(),
            "strong_confirmation_status": "NOT_REQUIRED_FOR_PREVIEW",
            "risk_level": risk_level,
            "write_mode": "PREVIEW_ONLY",
            "rollback_id": rollback_id,
            "before_state_hash": None,
            "before_state_ref": None,
            "after_state_hash": None,
            "after_state_ref": None,
            "side_effects_summary": _side_effects_summary(preview_result, audit_dry_run),
            "persistence_status": "RECORDED",
            "apply_allowed": False,
            "apply_executed": False,
            "failure_reason": None,
        }

    def _now_iso(self) -> str:
        value = self._clock()
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


def _blocked_result(
    *,
    audit_event_id: str | None,
    errors: list[str],
    rollback_id: str | None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "capability": CAPABILITY,
        "audit_event_id": audit_event_id or "",
        "rollback_id": rollback_id or "",
        "write_mode": "PREVIEW_ONLY",
        "apply_allowed": False,
        "apply_executed": False,
        "persistence_status": "BLOCKED",
        "repository_result": None,
        "record": None,
        "error": "validation_failed",
        "failure_reason": ";".join(errors),
    }


def _risk_level(preview_result: Any, audit_dry_run: Any) -> str:
    if isinstance(preview_result, dict) and preview_result.get("risk_level"):
        return str(preview_result["risk_level"]).upper()
    if isinstance(audit_dry_run, dict) and audit_dry_run.get("risk_level"):
        return str(audit_dry_run["risk_level"]).upper()
    return BLOCKED_RISK_LEVEL


def _side_effects_summary(
    preview_result: dict[str, Any],
    audit_dry_run: dict[str, Any],
) -> dict[str, bool]:
    value = preview_result.get("side_effects")
    if not isinstance(value, dict):
        value = audit_dry_run.get("side_effects")
    expected = {
        "db_write": False,
        "smf_write": False,
        "planner_update": False,
        "file_write": False,
        "external_call": False,
        "ocr": False,
        "ai_runtime": False,
    }
    if not isinstance(value, dict):
        return expected
    return {key: bool(value.get(key, False)) for key in expected}


def _stable_reference(prefix: str, value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def _default_audit_event_id() -> str:
    return f"audit-{uuid4().hex}"


def _default_rollback_id() -> str:
    return f"rollback-{uuid4().hex}"
