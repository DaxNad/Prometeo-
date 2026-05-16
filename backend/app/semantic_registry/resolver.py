from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .confidence_registry import get_confidence_entry
from .contracts import normalize_key
from .execution_readiness_registry import EXECUTION_READINESS_REGISTRY
from .governance_registry import AUTHORITY_PRECEDENCE
from .semantic_gate_registry import SEMANTIC_GATE_REGISTRY


SEMANTIC_RESOLVER_VERSION = "A1.5"


@dataclass(frozen=True)
class SemanticResolution:
    requested_key: str
    normalized_key: str
    registry: str
    authority: str
    master_refs: tuple[str, ...]
    fallback_applied: bool
    fallback_behavior: str
    contradiction_handling: str
    query_flow: tuple[str, ...]
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_confidence(value: Any) -> SemanticResolution:
    normalized = normalize_key(value)
    entry = get_confidence_entry(normalized)
    fallback_applied = entry.key != normalized
    return SemanticResolution(
        requested_key=str(value or ""),
        normalized_key=entry.key,
        registry="confidence_registry",
        authority=entry.authority,
        master_refs=entry.master_refs,
        fallback_applied=fallback_applied,
        fallback_behavior="fallback: unknown confidence resolves to DA_VERIFICARE",
        contradiction_handling="do not promote if any higher-authority source disagrees",
        query_flow=(
            "normalize input",
            "check canonical key and aliases",
            "return entry or DA_VERIFICARE fallback",
            "defer runtime action to semantic gates",
        ),
        payload=entry.to_dict(),
    )


def registry_lookup_boundaries() -> dict[str, Any]:
    return {
        "version": SEMANTIC_RESOLVER_VERSION,
        "authority_precedence": [boundary.to_dict() for boundary in AUTHORITY_PRECEDENCE],
        "lookup_boundaries": {
            "allowed_now": (
                "read canonical registry entries",
                "normalize confidence and operational-class labels",
                "explain fallback and authority references",
            ),
            "not_implemented_now": (
                "runtime execution rewiring",
                "planner rewrite",
                "automatic persistence of resolved semantics",
            ),
        },
        "fallback_behavior": {
            "unknown_confidence": "DA_VERIFICARE",
            "unknown_gate": "raise lookup error in registry accessors",
            "contradiction": "block stabilization and escalate to TL/governance",
        },
        "registry_query_flow": (
            "PROMETEO_MASTER authority check",
            "registry-specific lookup",
            "semantic gate readiness check",
            "explainability sufficiency check",
            "runtime module consumes result without mutating registry",
        ),
        "prepared_registries": {
            "semantic_gates": tuple(SEMANTIC_GATE_REGISTRY),
            "execution_readiness": tuple(EXECUTION_READINESS_REGISTRY),
        },
    }
