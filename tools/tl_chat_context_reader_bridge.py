from __future__ import annotations

from typing import Any

from tools.context_source_reader_adapter import (
    ContextSourceReaderAdapter,
    ContextSourceReaderError,
)
from backend.app.services.tl_chat_context_resolver import TLChatContextCandidate


def _map_reader_error_to_source_status(error_code: str) -> str:
    if error_code == "SOURCE_NOT_FOUND":
        return "SOURCE_MISSING"

    if error_code in {
        "SOURCE_FILE_NOT_FOUND",
        "INDEX_NOT_FOUND",
        "INDEX_INVALID",
        "NO_SOURCES_DECLARED",
    }:
        return "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"

    if error_code in {
        "SOURCE_ID_INVALID",
        "SOURCE_NOT_ALLOWED",
        "RUNTIME_SOURCE_BLOCKED",
        "SOURCE_PATH_MISSING",
        "FORBIDDEN_PATH_BLOCKED",
    }:
        return "SOURCE_FORBIDDEN"

    if error_code == "PATH_TRAVERSAL_BLOCKED":
        return "PATH_TRAVERSAL_BLOCKED"

    return "SOURCE_AUTHORIZED_BUT_UNAVAILABLE"


def build_context_reader_candidate(
    *,
    source_id: str,
    article: str,
    adapter: ContextSourceReaderAdapter | None = None,
    include_excerpt: bool = True,
    max_chars: int = 500,
) -> TLChatContextCandidate:
    """
    Minimal governed bridge between ContextSourceReaderAdapter and TL Chat resolver.

    Contract:
    - accepts only logical source_id
    - delegates read governance to ContextSourceReaderAdapter
    - returns a TLChatContextCandidate
    - never marks content as CERTO
    - never makes planner output eligible
    - never mutates application state
    """
    reader = adapter or ContextSourceReaderAdapter(max_chars=max_chars)

    try:
        result = (
            reader.read_excerpt(source_id)
            if include_excerpt
            else reader.read_metadata(source_id)
        )

        payload: dict[str, Any] = {
            "article": str(article or "").strip().upper(),
            "source_id": result.source_id,
            "reader_status": result.status,
            "metadata": result.metadata,
        }

        if result.content is not None:
            payload["excerpt"] = result.content

        return TLChatContextCandidate(
            source_name="context_source_reader_adapter",
            source_status="SOURCE_FOUND",
            confidence="DA_VERIFICARE",
            payload=payload,
            planner_eligible=False,
            requires_tl_confirmation=True,
        )

    except ContextSourceReaderError as exc:
        return TLChatContextCandidate(
            source_name="context_source_reader_adapter",
            source_status=_map_reader_error_to_source_status(exc.code),
            confidence="DA_VERIFICARE",
            payload={
                "article": str(article or "").strip().upper(),
                "source_id": source_id,
                "error_code": exc.code,
            },
            planner_eligible=False,
            requires_tl_confirmation=True,
        )
