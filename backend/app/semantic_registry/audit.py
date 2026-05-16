from __future__ import annotations

from dataclasses import asdict, dataclass

from .accessor import (
    resolve_semantic_confidence,
    resolve_semantic_gate,
    semantic_accessor_boundaries,
)
from .contracts import RegistryClassification


SEMANTIC_AUDIT_VERSION = "A1.5"
SEMANTIC_ACCESSOR_AUDIT_VERSION = "A5.2"


@dataclass(frozen=True)
class RuntimeSemanticFinding:
    area: str
    semantics: tuple[str, ...]
    classification: RegistryClassification
    evidence: tuple[str, ...]
    extraction_target: str
    stabilization_note: str

    def to_dict(self) -> dict:
        return asdict(self)


RUNTIME_SEMANTIC_AUDIT: tuple[RuntimeSemanticFinding, ...] = (
    RuntimeSemanticFinding(
        area="backend/app/api/tl_chat.py",
        semantics=("confidence", "HITL", "execution_readiness", "explainability"),
        classification="DUPLICATED",
        evidence=(
            "manual confidence defaults to DA_VERIFICARE",
            "route_status != CERTO requires confirmation",
            "INFERITO and DA_VERIFICARE produce repeated TL-safe action text",
        ),
        extraction_target="confidence_registry + semantic_gate_registry",
        stabilization_note="Runtime should progressively query confidence and TL confirmation gates.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/api/real_ingest.py",
        semantics=("validation", "confidence", "semantic_gate"),
        classification="HARD_CODED",
        evidence=(
            "code validation emits CERTO, INFERITO_DA_BOM and DA_VERIFICARE inline",
            "blocking_errors and warnings encode execution admissibility",
        ),
        extraction_target="validation_registry + confidence_registry",
        stabilization_note="Keep current behavior stable; future normalization should map INFERITO_DA_BOM to INFERITO with source BOM.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/domain/operational_class.py",
        semantics=("planner_admission", "confidence", "execution_readiness"),
        classification="PARTIAL",
        evidence=(
            "planner gate already explains rejected prerequisites",
            "STANDARD and REFERENCE_ONLY are normalized locally",
        ),
        extraction_target="semantic_gate_registry + execution_readiness_registry",
        stabilization_note="Existing gate is compatible with canonical registry and can become first resolver consumer.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/agent_runtime/architecture_guard.py",
        semantics=("governance", "semantic_gate", "explainability", "registry_impact"),
        classification="CANONICAL",
        evidence=(
            "detects Order -> ProductionEvent model risk",
            "marks semantic registry and planner impacts for review",
        ),
        extraction_target="governance_registry + validation_registry",
        stabilization_note="Guard concepts align with MASTER; registry should become the named authority layer.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/agent_runtime/decision_engine.py",
        semantics=("escalation", "HITL"),
        classification="HARD_CODED",
        evidence=(
            "possible_anomaly directly maps to local-escalation/investigate",
            "normal condition directly maps to monitor",
        ),
        extraction_target="escalation_registry",
        stabilization_note="Future resolver should choose escalation category while preserving local fallback.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/agent_runtime/policy.py",
        semantics=("escalation", "severity"),
        classification="DUPLICATED",
        evidence=("high/critical and possible_anomaly trigger escalation inline",),
        extraction_target="escalation_registry",
        stabilization_note="Severity thresholds need canonical naming before runtime rewiring.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/atlas_engine/decision_merge_engine.py",
        semantics=("contradiction", "explainability", "confidence", "semantic_gate"),
        classification="PARTIAL",
        evidence=(
            "constraint precedence and conflicts are explicit",
            "numeric confidence is normalized separately from canonical confidence states",
        ),
        extraction_target="explainability_registry + validation_registry",
        stabilization_note="Keep merge scoring intact; bind conflict explanation to canonical contradiction handling later.",
    ),
    RuntimeSemanticFinding(
        area="backend/app/services/explainability.py and sequence_explain.py",
        semantics=("explainability", "risk"),
        classification="PARTIAL",
        evidence=(
            "TL-readable reasons exist",
            "minimum sufficiency is not centrally named",
        ),
        extraction_target="explainability_registry",
        stabilization_note="Registry now names the minimum explanation bases without changing response payloads.",
    ),
)


def runtime_semantic_audit_as_dict() -> list[dict]:
    return [finding.to_dict() for finding in RUNTIME_SEMANTIC_AUDIT]


def semantic_accessor_audit_as_dict() -> dict:
    confidence_states = (
        "CERTO",
        "INFERITO",
        "DA_VERIFICARE",
        "BLOCCATO",
        "STANDARD",
        "REFERENCE_ONLY",
    )
    semantic_gates = (
        "PLANNER_ADMISSION_GATE",
        "TL_CONFIRMATION_GATE",
    )

    confidence_results = {
        key: resolve_semantic_confidence(key) for key in confidence_states
    }
    gate_results = {
        key: resolve_semantic_gate(key) for key in semantic_gates
    }
    unknown_confidence = resolve_semantic_confidence("UNKNOWN_CONFIDENCE")
    unknown_gate = resolve_semantic_gate("UNKNOWN_GATE")
    boundaries = semantic_accessor_boundaries()

    return {
        "version": SEMANTIC_ACCESSOR_AUDIT_VERSION,
        "read_only": True,
        "no_runtime_mutation": True,
        "no_planner_behavior_change": True,
        "no_execution_authority": True,
        "confidence_states": confidence_results,
        "semantic_gates": gate_results,
        "unknown_confidence_fallback": {
            "input": "UNKNOWN_CONFIDENCE",
            "normalized_key": unknown_confidence["normalized_key"],
            "fallback_applied": unknown_confidence["fallback_applied"],
        },
        "unknown_gate_fallback": {
            "input": "UNKNOWN_GATE",
            "normalized_key": unknown_gate["normalized_key"],
            "fallback_applied": unknown_gate["fallback_applied"],
            "admitted": unknown_gate["admitted"],
        },
        "boundaries": {
            "read_only": boundaries["read_only"],
            "no_runtime_mutation": boundaries["no_runtime_mutation"],
            "no_planner_behavior_change": boundaries["no_planner_behavior_change"],
            "no_execution_authority": boundaries["no_execution_authority"],
        },
    }
