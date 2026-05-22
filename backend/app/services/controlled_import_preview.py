from __future__ import annotations

from datetime import date
from typing import Any


WRITE_MODE = "PREVIEW_ONLY"
REQUIRED_FIELDS = ("order_id", "article_code", "quantity")
ALLOWED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "BLOCKED"}
KNOWN_STATIONS = {"ZAW-1", "ZAW-2", "PIDMILL", "HENN", "FORNO", "WINTEC", "ULTRASUONI", "CP"}
STATION_ALIASES = {
    "ZAW1": "ZAW-1",
    "ZAW 1": "ZAW-1",
    "ZAW_1": "ZAW-1",
    "ZAW-1": "ZAW-1",
    "ZAW2": "ZAW-2",
    "ZAW 2": "ZAW-2",
    "ZAW_2": "ZAW-2",
    "ZAW-2": "ZAW-2",
    "PIDMILL": "PIDMILL",
    "HENN": "HENN",
    "FORNO": "FORNO",
    "WINTEC": "WINTEC",
    "ULTRASUONI": "ULTRASUONI",
    "CP": "CP",
}
SENSITIVE_MARKERS = (
    "specs_finitura",
    "data/local_smf",
    "supermegafile",
    ".env",
    "token",
    "secret",
    "password",
    "/users/",
    "\\users\\",
    ".xlsx",
    ".xls",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
)


def build_controlled_import_preview(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Build a no-side-effect import preview from sanitized/demo input.

    This function must stay pure: no DB, no SMF, no planner, no file writes,
    no OCR, no AI and no network calls.
    """
    if not isinstance(payload, dict):
        return _blocked_response(
            errors=["payload_must_be_object"],
            preview={},
            warnings=[],
        )

    normalized, warnings = _normalize_payload(payload)
    errors = _validate_normalized(normalized)
    sensitive_hits = _find_sensitive_markers(payload)
    if sensitive_hits:
        errors.append("sensitive_input_detected")
        warnings.extend(f"sensitive_marker:{item}" for item in sensitive_hits)

    risk_level = _classify_risk(normalized=normalized, errors=errors, warnings=warnings)

    return {
        "ok": not errors,
        "capability": "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1",
        "write_mode": WRITE_MODE,
        "preview_only": True,
        "required_human_confirmation": True,
        "risk_level": risk_level,
        "risk_allowed_values": sorted(ALLOWED_RISK_LEVELS),
        "errors": errors,
        "warnings": warnings,
        "preview": normalized if not errors or risk_level != "BLOCKED" else {},
        "side_effects": {
            "db_write": False,
            "smf_write": False,
            "planner_update": False,
            "file_write": False,
            "external_call": False,
            "ocr": False,
            "ai_runtime": False,
        },
    }


def _normalize_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    route, route_warnings = _normalize_route(payload.get("route"))
    warnings.extend(route_warnings)

    quantity, quantity_warning = _normalize_quantity(payload.get("quantity", payload.get("qta")))
    if quantity_warning:
        warnings.append(quantity_warning)

    due_date, due_date_warning = _normalize_due_date(payload.get("due_date"))
    if due_date_warning:
        warnings.append(due_date_warning)

    source_type = _clean(payload.get("source_type")) or "synthetic"
    if source_type.lower() not in {"synthetic", "sanitized", "demo"}:
        warnings.append("source_type_not_explicitly_safe")

    return {
        "order_id": _clean(payload.get("order_id")),
        "article_code": _clean(payload.get("article_code", payload.get("codice"))),
        "quantity": quantity,
        "due_date": due_date,
        "priority": _clean(payload.get("priority")) or "MEDIA",
        "route": route,
        "station": _normalize_station(payload.get("station", payload.get("postazione"))),
        "note": _sanitize_note(payload.get("note")),
        "source_type": source_type,
    }, warnings


def _validate_normalized(normalized: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        value = normalized.get(field)
        if value is None or value == "":
            errors.append(f"missing_required_field:{field}")

    if normalized.get("quantity") is not None and normalized["quantity"] <= 0:
        errors.append("quantity_must_be_positive")

    route = normalized.get("route") or []
    unknown = [station for station in route if station not in KNOWN_STATIONS]
    if unknown:
        errors.append("unknown_route_station:" + ",".join(unknown))

    station = normalized.get("station")
    if station and station not in KNOWN_STATIONS:
        errors.append("unknown_station:" + station)

    return errors


def _classify_risk(
    *,
    normalized: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> str:
    if errors:
        return "BLOCKED"
    if any(item.startswith("source_type_not_explicitly_safe") for item in warnings):
        return "HIGH"
    if not normalized.get("route") or warnings:
        return "MEDIUM"
    return "LOW"


def _normalize_quantity(value: Any) -> tuple[float | None, str | None]:
    if value is None or _clean(value) == "":
        return None, None
    try:
        quantity = float(str(value).replace(",", "."))
    except ValueError:
        return None, "quantity_not_numeric"
    return quantity, None


def _normalize_due_date(value: Any) -> tuple[str | None, str | None]:
    raw = _clean(value)
    if not raw:
        return None, None
    try:
        return date.fromisoformat(raw).isoformat(), None
    except ValueError:
        return raw, "due_date_not_iso"


def _normalize_route(value: Any) -> tuple[list[str], list[str]]:
    if value is None or value == "":
        return [], []
    if not isinstance(value, list):
        return [], ["route_must_be_list"]
    return [_normalize_station(item) for item in value if _clean(item)], []


def _normalize_station(value: Any) -> str:
    raw = _clean(value).upper()
    return STATION_ALIASES.get(raw, raw)


def _sanitize_note(value: Any) -> str:
    note = _clean(value)
    if len(note) > 240:
        return note[:240]
    return note


def _find_sensitive_markers(payload: dict[str, Any]) -> list[str]:
    text = repr(payload).lower()
    return [marker for marker in SENSITIVE_MARKERS if marker in text]


def _blocked_response(
    *,
    errors: list[str],
    preview: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "ok": False,
        "capability": "CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1",
        "write_mode": WRITE_MODE,
        "preview_only": True,
        "required_human_confirmation": True,
        "risk_level": "BLOCKED",
        "risk_allowed_values": sorted(ALLOWED_RISK_LEVELS),
        "errors": errors,
        "warnings": warnings,
        "preview": preview,
        "side_effects": {
            "db_write": False,
            "smf_write": False,
            "planner_update": False,
            "file_write": False,
            "external_call": False,
            "ocr": False,
            "ai_runtime": False,
        },
    }


def _clean(value: Any) -> str:
    return str(value or "").strip()
