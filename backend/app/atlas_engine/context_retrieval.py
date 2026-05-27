"""
PROMETEO_AI_CONTEXT_RETRIEVAL_001

Read-only, local-only, preview-only context pack builder.

Scope v1:
- TL memory rules only
- no planner mutation
- no DB writes
- no SMF writes
- no LLM calls
"""

from __future__ import annotations

from typing import Any

from backend.app.atlas_engine.tl_memory.memory_retriever import retrieve_relevant_rules


PREVIEW_CONFIDENCE = "PREVIEW_ONLY"


def build_context_pack(question: str, limit: int = 5) -> dict[str, Any]:
    """Build a deterministic local context pack for a TL question.

    This function is intentionally read-only and does not call an LLM.
    It only packages locally retrieved PROMETEO rules.
    """
    normalized_question = (question or "").strip()
    rules = retrieve_relevant_rules(normalized_question, limit=limit)

    sources = []
    chunks = []

    for rule in rules:
        rule_id = str(rule.get("id", "")).strip()
        rule_text = str(rule.get("rule", "")).strip()
        priority = str(rule.get("priority", "low")).strip() or "low"
        tags = [str(tag) for tag in rule.get("tags", [])]

        if not rule_id or not rule_text:
            continue

        source = f"backend/app/atlas_engine/tl_memory/rules.json#{rule_id}"
        sources.append(source)
        chunks.append(
            {
                "source": source,
                "kind": "tl_memory_rule",
                "priority": priority,
                "tags": tags,
                "text": rule_text,
            }
        )

    return {
        "question": normalized_question,
        "confidence": PREVIEW_CONFIDENCE,
        "sources": sources,
        "chunks": chunks,
        "constraints": [
            "read-only",
            "local-only",
            "preview-only",
            "no planner mutation",
            "no DB writes",
            "no SMF writes",
            "no LLM calls",
        ],
    }
