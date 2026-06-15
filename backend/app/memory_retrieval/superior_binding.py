from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.memory_retrieval.context_pack import ContextPack
from backend.app.memory_retrieval.runtime_preview import (
    MemoryRetrievalRuntimeRequest,
    build_memory_retrieval_preview,
)


AUTHORIZED_CALLERS = frozenset({"runtime_preview"})
RESERVED_CALLERS = frozenset({"tl" + "_chat_preview", "atlas_preview"})

AUTHORIZED_INTENTS = frozenset(
    {
        "domain_memory_preview",
        "article_memory_preview",
        "rule_memory_preview",
    }
)
FORBIDDEN_INTENTS = frozenset(
    {
        "plan" + "ner_decision",
        "production_priority",
        "route_override",
        "metadata_update",
        "smf" + "_update",
        "memory_write",
        "llm" + "_answer_generation",
        "autonomous_decision",
    }
)

VIEW_ONLY = "VIEW_ONLY"
ASK_HUMAN_CONFIRMATION = "ASK_HUMAN_CONFIRMATION"
NO_ACTION = "NO_ACTION"
ALLOWED_NEXT_STEPS = frozenset({VIEW_ONLY, ASK_HUMAN_CONFIRMATION, NO_ACTION})


@dataclass(frozen=True)
class MemorySuperiorBindingRequest:
    query: str
    intent: str
    caller: str
    memory_root: Path
    dry_run: bool = True
    max_items: int = 5
    max_chars_per_item: int = 500


@dataclass(frozen=True)
class MemorySuperiorBindingResponse:
    ok: bool
    blocked: bool
    block_reason: str | None
    query: str
    intent: str
    caller: str
    context_pack: ContextPack | None
    allowed_next_step: str
    audit_reason: str


def build_memory_superior_binding_preview(
    request: MemorySuperiorBindingRequest,
) -> MemorySuperiorBindingResponse:
    block_reason = _validate_superior_request(request)
    if block_reason is not None:
        return _blocked_response(request, block_reason)

    runtime_response = build_memory_retrieval_preview(
        MemoryRetrievalRuntimeRequest(
            query=request.query,
            intent=request.intent,
            caller=request.caller,
            memory_root=request.memory_root,
            max_items=request.max_items,
            max_chars_per_item=request.max_chars_per_item,
            dry_run=True,
        )
    )

    if runtime_response.blocked:
        return _blocked_response(
            request,
            f"runtime_preview_blocked:{runtime_response.block_reason}",
            context_pack=runtime_response.context_pack,
        )

    context_pack = runtime_response.context_pack
    allowed_next_step = _allowed_next_step(request, context_pack)
    return MemorySuperiorBindingResponse(
        ok=True,
        blocked=False,
        block_reason=None,
        query=request.query,
        intent=request.intent,
        caller=request.caller,
        context_pack=context_pack,
        allowed_next_step=allowed_next_step,
        audit_reason=_audit_reason(request, allowed_next_step, context_pack),
    )


def _validate_superior_request(request: MemorySuperiorBindingRequest) -> str | None:
    caller = request.caller.strip()
    if not caller:
        return "missing_caller"
    if caller in RESERVED_CALLERS:
        return "reserved_caller_not_enabled"
    if caller not in AUTHORIZED_CALLERS:
        return "unauthorized_caller"

    intent = request.intent.strip()
    if not intent:
        return "missing_intent"
    if intent in FORBIDDEN_INTENTS:
        return "forbidden_intent"
    if intent not in AUTHORIZED_INTENTS:
        return "unauthorized_intent"

    if not request.query.strip():
        return "missing_query"

    if request.dry_run is not True:
        return "dry_run_required"

    if request.memory_root.name != "memory":
        return "invalid_memory_root"

    return None


def _allowed_next_step(
    request: MemorySuperiorBindingRequest,
    context_pack: ContextPack | None,
) -> str:
    if context_pack is None or context_pack.selected_count == 0:
        return NO_ACTION

    if request.intent == "article_memory_preview" and any(
        item.confidence != "CERTO" for item in context_pack.items
    ):
        return ASK_HUMAN_CONFIRMATION

    return VIEW_ONLY


def _blocked_response(
    request: MemorySuperiorBindingRequest,
    block_reason: str,
    context_pack: ContextPack | None = None,
) -> MemorySuperiorBindingResponse:
    return MemorySuperiorBindingResponse(
        ok=False,
        blocked=True,
        block_reason=block_reason,
        query=request.query,
        intent=request.intent,
        caller=request.caller,
        context_pack=context_pack,
        allowed_next_step=NO_ACTION,
        audit_reason=_audit_reason(request, NO_ACTION, context_pack),
    )


def _audit_reason(
    request: MemorySuperiorBindingRequest,
    allowed_next_step: str,
    context_pack: ContextPack | None,
) -> str:
    selected_count = context_pack.selected_count if context_pack is not None else 0
    return (
        "Memory superior binding preview requested by "
        f"caller={request.caller!r}, intent={request.intent!r}, "
        f"dry_run={request.dry_run}, allowed_next_step={allowed_next_step}, "
        f"selected_count={selected_count}."
    )
