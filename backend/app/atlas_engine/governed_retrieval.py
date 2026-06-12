from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.atlas_engine.context_retrieval import build_context_pack
from backend.app.semantic_registry.confidence_registry import confidence_registry_as_dict

MODE = "GOVERNED_RETRIEVAL_001"
PREVIEW_CONFIDENCE = "PREVIEW_ONLY"

CONSTRAINTS = (
    "read-only",
    "local-only",
    "no LLM calls",
    "no DB writes",
    "no SMF writes",
    "no planner mutation",
    "no runtime mutation",
    "no specs_finitura image access",
)

ALLOWED_SOURCES = (
    "tl_memory_rules",
    "docs/prometeo_system_map.md",
    "semantic_registry_confidence",
)

BLOCKED_SOURCES = (
    ".env",
    "specs_finitura_images",
    "real_smf",
    "real_excel",
    "database_dumps",
    "secrets",
)

ROOT = Path(__file__).resolve().parents[3]
SYSTEM_MAP = ROOT / "docs" / "prometeo_system_map.md"


def _evidence_item(*, source_id: str, source_type: str, authority_rank: int, confidence: str, text: str, reason: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_type": source_type,
        "authority_rank": authority_rank,
        "confidence": confidence,
        "text": text,
        "reason": reason,
    }


def _system_map_evidence(question: str) -> list[dict[str, Any]]:
    normalized = (question or "").strip().lower()
    if not normalized or not SYSTEM_MAP.exists():
        return []

    text = SYSTEM_MAP.read_text(encoding="utf-8")
    wanted_terms = ("zaw", "zaw1", "zaw2", "cp", "atlas", "planner", "fonte", "retrieval")
    if not any(term in normalized for term in wanted_terms):
        return []

    rows = []
    for line in text.splitlines():
        lower = line.lower()
        if any(term in lower for term in wanted_terms):
            rows.append(line.strip())
        if len(rows) >= 5:
            break

    if not rows:
        return []

    return [
        _evidence_item(
            source_id="docs/prometeo_system_map.md",
            source_type="system_map",
            authority_rank=20,
            confidence=PREVIEW_CONFIDENCE,
            text=" ".join(rows),
            reason="System map contains governed architecture and invariant rules relevant to the question.",
        )
    ]


def _tl_memory_evidence(question: str, limit: int) -> list[dict[str, Any]]:
    pack = build_context_pack(question, limit=limit)
    evidence = []
    for chunk in pack.get("chunks", []):
        source = str(chunk.get("source") or "").strip()
        text = str(chunk.get("text") or "").strip()
        if not source or not text:
            continue
        evidence.append(
            _evidence_item(
                source_id=source,
                source_type="tl_memory_rule",
                authority_rank=10,
                confidence=PREVIEW_CONFIDENCE,
                text=text,
                reason="Retrieved by existing local TL memory context retrieval.",
            )
        )
    return evidence


def _semantic_confidence_evidence(question: str) -> list[dict[str, Any]]:
    normalized = (question or "").strip().upper()
    if not normalized:
        return []

    trigger_terms = (
        "CONFIDENCE",
        "CERTO",
        "INFERITO",
        "DA_VERIFICARE",
        "DA VERIFICARE",
        "BLOCCATO",
        "STANDARD",
        "REFERENCE_ONLY",
        "REFERENCE",
        "CERTEZZA",
        "VERIFICA",
        "VERIFICARE",
    )
    if not any(term in normalized for term in trigger_terms):
        return []

    registry = confidence_registry_as_dict()
    wanted_keys = ("CERTO", "INFERITO", "DA_VERIFICARE")
    evidence: list[dict[str, Any]] = []

    for key in wanted_keys:
        entry = registry.get(key)
        if not entry:
            continue

        meaning = str(entry.get("meaning") or "").strip()
        execution_admissibility = str(entry.get("execution_admissibility") or "").strip()
        obligations = entry.get("obligations") or ()
        obligations_text = "; ".join(str(item) for item in obligations if item)

        parts = [f"{key}: {meaning}"]
        if execution_admissibility:
            parts.append(f"Admissibility: {execution_admissibility}")
        if obligations_text:
            parts.append(f"Obligations: {obligations_text}")

        evidence.append(
            _evidence_item(
                source_id=f"semantic_registry_confidence:{key}",
                source_type="semantic_registry_confidence",
                authority_rank=15,
                confidence=PREVIEW_CONFIDENCE,
                text=" ".join(parts),
                reason="Canonical confidence semantics from semantic registry.",
            )
        )

    return evidence


def build_governed_retrieval_pack(question: str, article: str | None = None, limit: int = 5) -> dict[str, Any]:
    normalized_question = (question or "").strip()
    safe_limit = max(0, min(int(limit), 10))

    evidence: list[dict[str, Any]] = []
    if normalized_question and safe_limit > 0:
        system_map_evidence = _system_map_evidence(normalized_question)
        semantic_confidence_evidence = _semantic_confidence_evidence(normalized_question)
        tl_memory_evidence = _tl_memory_evidence(normalized_question, safe_limit)

        evidence.extend(system_map_evidence[:safe_limit])
        remaining_slots = max(0, safe_limit - len(evidence))
        evidence.extend(semantic_confidence_evidence[:remaining_slots])
        remaining_slots = max(0, safe_limit - len(evidence))
        evidence.extend(tl_memory_evidence[:remaining_slots])

    return {
        "mode": MODE,
        "question": normalized_question,
        "article": (article or None),
        "evidence": evidence,
        "constraints": list(CONSTRAINTS),
        "allowed_sources": list(ALLOWED_SOURCES),
        "blocked_sources": list(BLOCKED_SOURCES),
    }
