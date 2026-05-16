from __future__ import annotations

from typing import Any

from .confidence_registry import get_confidence_entry
from .contracts import normalize_key
from .resolver import registry_lookup_boundaries
from .semantic_gate_registry import get_semantic_gate_entry


SEMANTIC_ACCESSOR_VERSION = "A5"


def resolve_semantic_confidence(value: str) -> dict[str, Any]:
    entry = get_confidence_entry(value)
    normalized = normalize_key(value)
    fallback_applied = entry.key != normalized

    return {
        "version": SEMANTIC_ACCESSOR_VERSION,
        "registry": "confidence_registry",
        "requested_key": str(value or ""),
        "normalized_key": entry.key,
        "fallback_applied": fallback_applied,
        "read_only": True,
        "no_runtime_mutation": True,
        "entry": entry.to_dict(),
    }


def resolve_semantic_gate(value: str) -> dict[str, Any]:
    normalized = normalize_key(value)
    try:
        entry = get_semantic_gate_entry(normalized)
    except KeyError:
        return {
            "version": SEMANTIC_ACCESSOR_VERSION,
            "registry": "semantic_gate_registry",
            "requested_key": str(value or ""),
            "normalized_key": normalized,
            "fallback_applied": True,
            "read_only": True,
            "no_runtime_mutation": True,
            "admitted": False,
            "diagnostic": "unknown semantic gate; no runtime authority granted",
            "entry": None,
        }

    return {
        "version": SEMANTIC_ACCESSOR_VERSION,
        "registry": "semantic_gate_registry",
        "requested_key": str(value or ""),
        "normalized_key": entry.key,
        "fallback_applied": False,
        "read_only": True,
        "no_runtime_mutation": True,
        "admitted": None,
        "entry": entry.to_dict(),
    }


def semantic_accessor_boundaries() -> dict[str, Any]:
    boundaries = registry_lookup_boundaries()
    return {
        "version": SEMANTIC_ACCESSOR_VERSION,
        "read_only": True,
        "no_runtime_mutation": True,
        "no_planner_behavior_change": True,
        "no_execution_authority": True,
        "confidence_fallback": "DA_VERIFICARE",
        "unknown_gate_behavior": "diagnostic_fallback_without_exception",
        "registry_boundaries": boundaries,
    }
