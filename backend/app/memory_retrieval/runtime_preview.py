from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.memory_retrieval.binding import collect_memory_evidence
from backend.app.memory_retrieval.context_pack import ContextPack, build_context_pack


@dataclass(frozen=True)
class MemoryRetrievalRuntimeRequest:
    query: str
    intent: str
    caller: str
    memory_root: Path
    max_items: int = 5
    max_chars_per_item: int = 500
    dry_run: bool = True


@dataclass(frozen=True)
class MemoryRetrievalRuntimeResponse:
    ok: bool
    blocked: bool
    block_reason: str | None
    context_pack: ContextPack | None
    audit_reason: str


def build_memory_retrieval_preview(
    request: MemoryRetrievalRuntimeRequest,
) -> MemoryRetrievalRuntimeResponse:
    block_reason = _validate_request(request)
    if block_reason is not None:
        return _blocked_response(request, block_reason)

    query = request.query.strip()
    evidence = collect_memory_evidence(request.memory_root, query=query)
    context_pack = build_context_pack(
        evidence,
        query=query,
        max_items=request.max_items,
        max_chars_per_item=request.max_chars_per_item,
    )

    block_reason = _validate_context_pack(context_pack)
    if block_reason is not None:
        return _blocked_response(request, block_reason)

    return MemoryRetrievalRuntimeResponse(
        ok=True,
        blocked=False,
        block_reason=None,
        context_pack=context_pack,
        audit_reason=_audit_reason(request, context_pack.selected_count),
    )


def _validate_request(request: MemoryRetrievalRuntimeRequest) -> str | None:
    if request.dry_run is not True:
        return "dry_run must be true for preview-only runtime."

    if not request.query.strip():
        return "query is empty or not classified."

    if not request.intent.strip():
        return "intent is empty or not classified."

    if not request.caller.strip():
        return "caller is empty or not declared."

    if not request.memory_root.exists():
        return "memory_root does not exist."

    if not request.memory_root.is_dir():
        return "memory_root is not a directory."

    if request.memory_root.name != "memory":
        return "memory_root must point to an authorized memory directory."

    return None


def _validate_context_pack(context_pack: ContextPack) -> str | None:
    for item in context_pack.items:
        if not item.source_path.startswith("memory/"):
            return "context_pack contains source_path outside memory/."

        if not item.authority.strip():
            return "context_pack contains item with missing authority."

        if not item.confidence.strip():
            return "context_pack contains item with missing confidence."

    return None


def _blocked_response(
    request: MemoryRetrievalRuntimeRequest,
    block_reason: str,
) -> MemoryRetrievalRuntimeResponse:
    return MemoryRetrievalRuntimeResponse(
        ok=False,
        blocked=True,
        block_reason=block_reason,
        context_pack=None,
        audit_reason=_audit_reason(request, selected_count=0),
    )


def _audit_reason(request: MemoryRetrievalRuntimeRequest, selected_count: int) -> str:
    return (
        "Memory retrieval preview requested by "
        f"caller={request.caller!r}, intent={request.intent!r}, "
        f"dry_run={request.dry_run}, query={request.query!r}; "
        f"selected_count={selected_count}."
    )
