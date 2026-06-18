from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "PROMETEO_CONTEXT_SOURCE_INDEX_001"
EXPECTED_STATUS = "documental_index_only"

ALLOWED_SOURCE_PREFIXES = (
    "docs/",
    "memory/",
)

FORBIDDEN_SOURCE_PREFIXES = (
    ".env",
    "backend/",
    "frontend/",
    "runtime/",
    "planner/",
    "database/",
    "data/local_smf",
    "data/export",
    "specs_finitura/",
    "node_modules/",
    "venv/",
    ".venv/",
)

class ContextSourceReaderAdapterError(ValueError):
    """Raised only for invalid adapter input, not for invalid index content."""


def read_context_source_index(
    index_path: str | Path,
    *,
    allowed_for: str | None = None,
    source_ids: list[str] | tuple[str, ...] | None = None,
    max_sources: int | None = None,
    include_bytes: bool = False,
) -> dict[str, Any]:
    """
    Read the governed context source index in read-only mode.

    This adapter intentionally returns only minimal source metadata.
    It does not open indexed source files, does not bind runtime, and does not
    import TL Chat, ATLAS, planner, FastAPI app, LLM, DB or executor modules.
    """
    if max_sources is not None and max_sources < 0:
        raise ContextSourceReaderAdapterError("max_sources must be >= 0")

    requested_source_ids = tuple(source_ids or ())
    path = Path(index_path)

    if not path.is_file():
        return _blocked_result("INDEX_MISSING", f"index not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _blocked_result("JSON_MALFORMED", f"malformed JSON: {exc.msg}")

    validation_errors = _validate_index_root(data)
    if validation_errors:
        return {
            "ok": False,
            "mode": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
            "schema": data.get("schema") if isinstance(data, dict) else None,
            "status": data.get("status") if isinstance(data, dict) else None,
            "runtime_enabled": data.get("runtime_enabled") if isinstance(data, dict) else None,
            "sources": [],
            "rejected": [],
            "warnings": [],
            "errors": validation_errors,
        }

    sources = data["sources"]
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    known_ids = {
        source.get("id")
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }

    for requested_id in requested_source_ids:
        if requested_id not in known_ids:
            rejected.append({
                "id": requested_id,
                "reason": "SOURCE_ID_NOT_FOUND",
            })

    for source in sources:
        normalized, reason = _normalize_source(source, include_bytes=include_bytes)

        if normalized is None:
            rejected.append({
                "id": source.get("id") if isinstance(source, dict) else None,
                "reason": reason,
            })
            continue

        if requested_source_ids and normalized["id"] not in requested_source_ids:
            continue

        if allowed_for is not None and allowed_for not in normalized["allowed_for"]:
            rejected.append({
                "id": normalized["id"],
                "reason": "ALLOWED_FOR_FILTERED_OUT",
            })
            continue

        selected.append(normalized)

    if max_sources is not None:
        selected = selected[:max_sources]

    return {
        "ok": True,
        "mode": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
        "schema": data["schema"],
        "status": data["status"],
        "runtime_enabled": False,
        "sources": selected,
        "rejected": rejected,
        "warnings": [],
        "errors": [],
    }


def _blocked_result(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "mode": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
        "schema": None,
        "status": None,
        "runtime_enabled": None,
        "sources": [],
        "rejected": [],
        "warnings": [],
        "errors": [{"code": code, "message": message}],
    }


def _validate_index_root(data: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    if not isinstance(data, dict):
        return [{"code": "SCHEMA_INVALID", "message": "index root must be an object"}]

    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append({
            "code": "SCHEMA_INVALID",
            "message": "unsupported context source index schema",
        })

    if data.get("status") != EXPECTED_STATUS:
        errors.append({
            "code": "STATUS_INVALID",
            "message": "index status must be documental_index_only",
        })

    if data.get("runtime_enabled") is not False:
        errors.append({
            "code": "GLOBAL_RUNTIME_ENABLED",
            "message": "global runtime_enabled must be false",
        })

    if not isinstance(data.get("sources"), list):
        errors.append({
            "code": "SOURCES_INVALID",
            "message": "sources must be a list",
        })

    return errors


def _normalize_source(
    source: Any,
    *,
    include_bytes: bool,
) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(source, dict):
        return None, "SOURCE_NOT_OBJECT"

    source_id = source.get("id")
    source_path = source.get("path")
    allowed_for = source.get("allowed_for")

    if not isinstance(source_id, str) or not source_id.strip():
        return None, "SOURCE_ID_INVALID"

    if not isinstance(source_path, str) or not source_path.strip():
        return None, "SOURCE_PATH_INVALID"

    if not _is_allowed_relative_source_path(source_path):
        return None, "SOURCE_PATH_BLOCKED"

    if source.get("access_mode") != "read_only":
        return None, "ACCESS_MODE_NOT_READ_ONLY"

    if source.get("runtime_enabled") is not False:
        return None, "SOURCE_RUNTIME_ENABLED"

    if not isinstance(allowed_for, list) or not all(isinstance(item, str) for item in allowed_for):
        return None, "ALLOWED_FOR_INVALID"

    normalized = {
        "id": source_id,
        "path": source_path,
        "kind": source.get("kind"),
        "tier": source.get("tier"),
        "authority": source.get("authority"),
        "role": source.get("role"),
        "access_mode": "read_only",
        "runtime_enabled": False,
        "allowed_for": list(allowed_for),
        "exists": bool(source.get("exists")),
    }

    if include_bytes:
        normalized["bytes"] = source.get("bytes")

    return normalized, "OK"


def _is_allowed_relative_source_path(source_path: str) -> bool:
    normalized = source_path.replace("\\", "/").strip()

    if not normalized:
        return False

    if normalized.startswith("/"):
        return False

    parts = normalized.split("/")
    if ".." in parts:
        return False

    lowered = normalized.lower()

    if lowered == ".env" or lowered.startswith(".env/"):
        return False

    if any(lowered.startswith(prefix.lower()) for prefix in FORBIDDEN_SOURCE_PREFIXES):
        return False

    return any(normalized.startswith(prefix) for prefix in ALLOWED_SOURCE_PREFIXES)
