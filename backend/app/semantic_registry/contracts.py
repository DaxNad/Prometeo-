from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


RegistryClassification = Literal[
    "CANONICAL",
    "DUPLICATED",
    "PARTIAL",
    "HARD_CODED",
    "CONFLICTING",
]

RegistryAuthority = Literal[
    "PROMETEO_MASTER",
    "TL_CONFIRMATION",
    "REAL_SPEC",
    "DOMAIN_STRUCTURE",
    "RUNTIME_PREPARATION",
]


@dataclass(frozen=True)
class AuthorityBoundary:
    authority: RegistryAuthority
    precedence_rank: int
    reference: str
    responsibility: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegistryEntry:
    key: str
    meaning: str
    authority: RegistryAuthority
    master_refs: tuple[str, ...]
    obligations: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConfidenceEntry(RegistryEntry):
    escalation_behavior: str = ""
    execution_admissibility: str = ""
    validation_requirements: tuple[str, ...] = ()
    hitl_requirements: tuple[str, ...] = ()
    rollback_constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class EscalationEntry(RegistryEntry):
    triggers: tuple[str, ...] = ()
    severity: str = ""
    requires_tl_confirmation: bool = True
    blocks_execution: bool = False
    reversible: bool = True


@dataclass(frozen=True)
class ExplainabilityEntry(RegistryEntry):
    required_evidence: tuple[str, ...] = ()
    sufficiency_rule: str = ""


@dataclass(frozen=True)
class GovernanceEntry(RegistryEntry):
    precedence: int = 0
    admissibility_rule: str = ""
    rollback_rule: str = ""


@dataclass(frozen=True)
class ValidationEntry(RegistryEntry):
    validates: tuple[str, ...] = ()
    failure_mode: str = ""
    escalation_key: str = ""


@dataclass(frozen=True)
class SemanticGateEntry(RegistryEntry):
    inputs: tuple[str, ...] = ()
    pass_rule: str = ""
    fail_rule: str = ""


@dataclass(frozen=True)
class ExecutionReadinessEntry(RegistryEntry):
    required_states: tuple[str, ...] = ()
    blocking_states: tuple[str, ...] = ()
    tl_override_allowed: bool = True
    readiness_rule: str = ""


def normalize_key(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def registry_to_dict(entries: dict[str, RegistryEntry]) -> dict[str, dict[str, Any]]:
    return {key: entry.to_dict() for key, entry in entries.items()}
