from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from typing import Any


ALLOWED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "BLOCKED"}
ALLOWED_WRITE_MODES = {"PREVIEW_ONLY", "APPLY"}
ALLOWED_CONFIRMATION_STATUSES = {
    "NOT_REQUIRED_FOR_PREVIEW",
    "REQUIRED",
    "CONFIRMED",
    "MISSING",
    "INVALID",
}
ALLOWED_PERSISTENCE_STATUSES = {"PENDING", "RECORDED", "FAILED", "BLOCKED"}
FORBIDDEN_FIELDS = {
    "confirmation_token",
    "payload",
    "customer_data",
    "smf_payload",
    "bom_payload",
    "real_data",
}
SENSITIVE_MARKERS = (
    "specs_finitura",
    "data/local_smf",
    "supermegafile",
    ".env",
    "token=",
    "password",
    ".xlsx",
    ".xls",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
)
REQUIRED_FIELDS = (
    "audit_event_id",
    "audit_event_type",
    "actor",
    "source",
    "timestamp_utc",
    "preview_reference",
    "dry_run_reference",
    "confirmation_token_hash",
    "strong_confirmation_status",
    "risk_level",
    "write_mode",
    "rollback_id",
    "side_effects_summary",
    "persistence_status",
    "apply_allowed",
    "apply_executed",
)
COMPARABLE_FIELDS = REQUIRED_FIELDS + (
    "before_state_hash",
    "before_state_ref",
    "after_state_hash",
    "after_state_ref",
    "failure_reason",
)


class ControlledImportAuditRepository:
    def __init__(self, connection_factory: Callable[[], Any] | None = None) -> None:
        self._connection_factory = connection_factory

    def record_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized, errors = self._normalize_and_validate(payload)
        if errors:
            return {
                "ok": False,
                "audit_event_id": str(payload.get("audit_event_id") or ""),
                "persistence_status": "BLOCKED",
                "idempotent_replay": False,
                "error": "validation_failed",
                "failure_reason": ";".join(errors),
                "apply_allowed": bool(payload.get("apply_allowed", False)),
                "apply_executed": bool(payload.get("apply_executed", False)),
            }

        with self._connection() as conn:
            with conn.cursor() as cur:
                existing = self._fetch_existing(cur, normalized["audit_event_id"])
                if existing is not None:
                    if self._matches_existing(existing, normalized):
                        return {
                            "ok": True,
                            "audit_event_id": normalized["audit_event_id"],
                            "persistence_status": str(
                                existing.get("persistence_status") or "RECORDED"
                            ),
                            "created_at": existing.get("created_at"),
                            "idempotent_replay": True,
                            "error": None,
                            "failure_reason": None,
                            "apply_allowed": bool(existing.get("apply_allowed", False)),
                            "apply_executed": bool(existing.get("apply_executed", False)),
                        }
                    return {
                        "ok": False,
                        "audit_event_id": normalized["audit_event_id"],
                        "persistence_status": "FAILED",
                        "idempotent_replay": False,
                        "error": "audit_event_duplicate_conflict",
                        "failure_reason": "audit_event_id already exists with different content",
                        "apply_allowed": normalized["apply_allowed"],
                        "apply_executed": normalized["apply_executed"],
                    }

                self._insert(cur, normalized)
                conn.commit()

        return {
            "ok": True,
            "audit_event_id": normalized["audit_event_id"],
            "persistence_status": normalized["persistence_status"],
            "created_at": None,
            "idempotent_replay": False,
            "error": None,
            "failure_reason": normalized.get("failure_reason"),
            "apply_allowed": normalized["apply_allowed"],
            "apply_executed": normalized["apply_executed"],
        }

    def get_event(self, audit_event_id: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                return self._fetch_existing(cur, audit_event_id)

    def find_by_rollback_id(self, rollback_id: str) -> list[dict[str, Any]]:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM controlled_import_audit_events
                    WHERE rollback_id = %s
                    ORDER BY timestamp_utc ASC, created_at ASC
                    """,
                    (rollback_id,),
                )
                return [dict(row) for row in cur.fetchall()]

    def find_by_confirmation_token_hash(
        self,
        confirmation_token_hash: str,
    ) -> list[dict[str, Any]]:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM controlled_import_audit_events
                    WHERE confirmation_token_hash = %s
                    ORDER BY timestamp_utc ASC, created_at ASC
                    """,
                    (confirmation_token_hash,),
                )
                return [dict(row) for row in cur.fetchall()]

    def _connection(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        from app.db import get_postgres_connection

        return get_postgres_connection()

    def _fetch_existing(self, cur: Any, audit_event_id: str) -> dict[str, Any] | None:
        cur.execute(
            """
            SELECT *
            FROM controlled_import_audit_events
            WHERE audit_event_id = %s
            """,
            (audit_event_id,),
        )
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def _insert(self, cur: Any, event: dict[str, Any]) -> None:
        cur.execute(
            """
            INSERT INTO controlled_import_audit_events (
                audit_event_id,
                audit_event_type,
                actor,
                source,
                timestamp_utc,
                preview_reference,
                dry_run_reference,
                confirmation_token_hash,
                strong_confirmation_status,
                risk_level,
                write_mode,
                rollback_id,
                before_state_hash,
                before_state_ref,
                after_state_hash,
                after_state_ref,
                side_effects_summary,
                persistence_status,
                apply_allowed,
                apply_executed,
                failure_reason
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                event["audit_event_id"],
                event["audit_event_type"],
                event["actor"],
                event["source"],
                event["timestamp_utc"],
                event["preview_reference"],
                event["dry_run_reference"],
                event["confirmation_token_hash"],
                event["strong_confirmation_status"],
                event["risk_level"],
                event["write_mode"],
                event["rollback_id"],
                event.get("before_state_hash"),
                event.get("before_state_ref"),
                event.get("after_state_hash"),
                event.get("after_state_ref"),
                json.dumps(event["side_effects_summary"], sort_keys=True),
                event["persistence_status"],
                event["apply_allowed"],
                event["apply_executed"],
                event.get("failure_reason"),
            ),
        )

    def _normalize_and_validate(
        self,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], list[str]]:
        if not isinstance(payload, dict):
            return {}, ["payload_must_be_object"]

        errors: list[str] = []
        for field in REQUIRED_FIELDS:
            if field not in payload or payload[field] in (None, ""):
                errors.append(f"missing_required_field:{field}")

        forbidden_present = sorted(field for field in FORBIDDEN_FIELDS if field in payload)
        errors.extend(f"forbidden_field:{field}" for field in forbidden_present)

        sensitive_hits = self._find_sensitive_markers(payload)
        errors.extend(f"sensitive_marker:{marker}" for marker in sensitive_hits)

        risk_level = str(payload.get("risk_level") or "").upper()
        write_mode = str(payload.get("write_mode") or "").upper()
        confirmation_status = str(payload.get("strong_confirmation_status") or "").upper()
        persistence_status = str(payload.get("persistence_status") or "").upper()
        apply_allowed = bool(payload.get("apply_allowed", False))
        apply_executed = bool(payload.get("apply_executed", False))

        if risk_level and risk_level not in ALLOWED_RISK_LEVELS:
            errors.append("invalid_risk_level")
        if write_mode and write_mode not in ALLOWED_WRITE_MODES:
            errors.append("invalid_write_mode")
        if confirmation_status and confirmation_status not in ALLOWED_CONFIRMATION_STATUSES:
            errors.append("invalid_strong_confirmation_status")
        if persistence_status and persistence_status not in ALLOWED_PERSISTENCE_STATUSES:
            errors.append("invalid_persistence_status")
        if apply_executed and not apply_allowed:
            errors.append("invalid_apply_flags")
        if apply_executed and confirmation_status != "CONFIRMED":
            errors.append("strong_confirmation_required_for_apply")
        if apply_executed and not payload.get("confirmation_token_hash"):
            errors.append("confirmation_token_hash_required_for_apply")
        if apply_executed and not payload.get("rollback_id"):
            errors.append("rollback_id_required_for_apply")

        side_effects = payload.get("side_effects_summary")
        if not isinstance(side_effects, dict):
            errors.append("side_effects_missing")
            side_effects = {}

        timestamp_utc = str(payload.get("timestamp_utc") or "")
        if timestamp_utc:
            try:
                datetime.fromisoformat(timestamp_utc)
            except ValueError:
                errors.append("invalid_timestamp_utc")

        normalized = {
            "audit_event_id": str(payload.get("audit_event_id") or "").strip(),
            "audit_event_type": str(payload.get("audit_event_type") or "").strip(),
            "actor": str(payload.get("actor") or "").strip(),
            "source": str(payload.get("source") or "").strip(),
            "timestamp_utc": timestamp_utc,
            "preview_reference": str(payload.get("preview_reference") or "").strip(),
            "dry_run_reference": str(payload.get("dry_run_reference") or "").strip(),
            "confirmation_token_hash": str(payload.get("confirmation_token_hash") or "").strip(),
            "strong_confirmation_status": confirmation_status,
            "risk_level": risk_level,
            "write_mode": write_mode,
            "rollback_id": str(payload.get("rollback_id") or "").strip(),
            "before_state_hash": _optional_text(payload.get("before_state_hash")),
            "before_state_ref": _optional_text(payload.get("before_state_ref")),
            "after_state_hash": _optional_text(payload.get("after_state_hash")),
            "after_state_ref": _optional_text(payload.get("after_state_ref")),
            "side_effects_summary": side_effects,
            "persistence_status": persistence_status,
            "apply_allowed": apply_allowed,
            "apply_executed": apply_executed,
            "failure_reason": _optional_text(payload.get("failure_reason")),
        }
        return normalized, errors

    def _matches_existing(self, existing: dict[str, Any], event: dict[str, Any]) -> bool:
        for field in COMPARABLE_FIELDS:
            left = existing.get(field)
            right = event.get(field)
            if field == "side_effects_summary":
                left = _normalize_json(left)
                right = _normalize_json(right)
            if left != right:
                return False
        return True

    def _find_sensitive_markers(self, payload: dict[str, Any]) -> list[str]:
        text = repr(payload).lower()
        return [marker for marker in SENSITIVE_MARKERS if marker in text]


def _normalize_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    clean = str(value).strip()
    return clean or None
