from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


AUDIT_EVENT_TYPE = "CONTROLLED_IMPORT_PREVIEW_EVALUATED"
AUDIT_MODE = "DRY_RUN"


def build_controlled_import_audit_dry_run(preview_result: dict[str, Any]) -> dict[str, Any]:
    """
    Build a non-persistent audit trace for a controlled import preview.

    This function is intentionally pure: no DB writes, no file writes, no SMF,
    no planner updates, no external calls and no apply.
    """
    side_effects = _normalize_side_effects(preview_result.get("side_effects"))
    return {
        "ok": True,
        "capability": "CONTROLLED_IMPORT_AUDIT_DRY_RUN_V1",
        "audit_mode": AUDIT_MODE,
        "audit_event_type": AUDIT_EVENT_TYPE,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_capability": str(preview_result.get("capability") or ""),
        "preview_ok": bool(preview_result.get("ok")),
        "risk_level": str(preview_result.get("risk_level") or "BLOCKED"),
        "write_mode": str(preview_result.get("write_mode") or "PREVIEW_ONLY"),
        "human_confirmation_required": bool(
            preview_result.get("required_human_confirmation", True)
        ),
        "errors_count": len(preview_result.get("errors") or []),
        "warnings_count": len(preview_result.get("warnings") or []),
        "side_effects": side_effects,
        "persistence": {
            "db_write": False,
            "file_write": False,
            "smf_write": False,
            "planner_update": False,
        },
        "apply_allowed": False,
    }


def _normalize_side_effects(value: Any) -> dict[str, bool]:
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

    normalized = dict(expected)
    for key in expected:
        normalized[key] = bool(value.get(key, False))
    return normalized
