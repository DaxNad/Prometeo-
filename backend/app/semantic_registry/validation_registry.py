from __future__ import annotations

from .contracts import ValidationEntry, normalize_key, registry_to_dict


VALIDATION_REGISTRY_VERSION = "A1.5"

VALIDATION_REGISTRY: dict[str, ValidationEntry] = {
    "SEMANTIC_CONSISTENCY_VALIDATION": ValidationEntry(
        key="SEMANTIC_CONSISTENCY_VALIDATION",
        meaning="Verifica che stati, classi e fonti non siano incompatibili.",
        authority="PROMETEO_MASTER",
        master_refs=("MASTER-ANTIFRAG-001", "CONFIDENCE-SEMANTICS-001"),
        validates=("confidence", "operational_class", "route_status"),
        failure_mode="CONTRADICTION_ESCALATION",
        escalation_key="CONTRADICTION_ESCALATION",
    ),
    "PLANNER_COHERENCE_VALIDATION": ValidationEntry(
        key="PLANNER_COHERENCE_VALIDATION",
        meaning="Verifica che ammissione planner rispetti classe, route, domanda e blocker.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BOUNDARY-001", "PLANNER-BLOCKING-001"),
        validates=("planner_eligible", "route_status", "active_customer_order", "blocking_constraint"),
        failure_mode="BLOCKING_ESCALATION",
        escalation_key="BLOCKING_ESCALATION",
    ),
    "EXPLAINABILITY_VALIDATION": ValidationEntry(
        key="EXPLAINABILITY_VALIDATION",
        meaning="Verifica sufficienza minima della spiegazione tecnico-funzionale.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-EXPLAINABILITY-001", "AUTONOMIC-EXPLAINABILITY-001"),
        validates=("causal_basis", "confidence_basis", "governance_basis", "uncertainty_basis"),
        failure_mode="EXPLAINABILITY_ESCALATION",
        escalation_key="EXPLAINABILITY_ESCALATION",
    ),
    "CONFIDENCE_VALIDATION": ValidationEntry(
        key="CONFIDENCE_VALIDATION",
        meaning="Verifica che lo stato confidence sia canonico e coerente con la fonte.",
        authority="PROMETEO_MASTER",
        master_refs=("CONFIDENCE-SEMANTICS-001",),
        validates=("CERTO", "INFERITO", "DA_VERIFICARE", "BLOCCATO"),
        failure_mode="SOFT_ESCALATION",
        escalation_key="SOFT_ESCALATION",
    ),
    "GOVERNANCE_VALIDATION": ValidationEntry(
        key="GOVERNANCE_VALIDATION",
        meaning="Verifica rispetto di TL supremacy, bounded autonomy e authority precedence.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-AUTHORITY-001", "AUTONOMIC-GOVERNANCE-001"),
        validates=("tl_confirmation", "authority_precedence", "bounded_autonomy"),
        failure_mode="GOVERNANCE_ESCALATION",
        escalation_key="GOVERNANCE_ESCALATION",
    ),
    "ESCALATION_VALIDATION": ValidationEntry(
        key="ESCALATION_VALIDATION",
        meaning="Verifica che escalation sia bounded, spiegabile, reversibile e TL-governed.",
        authority="PROMETEO_MASTER",
        master_refs=("STRATEGIC-HITL-001", "OPERATIONAL-RISK-001"),
        validates=("trigger", "severity", "tl_confirmation", "rollback"),
        failure_mode="GOVERNANCE_ESCALATION",
        escalation_key="GOVERNANCE_ESCALATION",
    ),
    "CONTRADICTION_VALIDATION": ValidationEntry(
        key="CONTRADICTION_VALIDATION",
        meaning="Verifica disaccordi tra moduli, fonti e segnali runtime.",
        authority="PROMETEO_MASTER",
        master_refs=("COGNITIVE-INTEGRITY-001", "MASTER-ANTIFRAG-001"),
        validates=("source_conflict", "module_disagreement", "decision_conflict"),
        failure_mode="CONTRADICTION_ESCALATION",
        escalation_key="CONTRADICTION_ESCALATION",
    ),
    "SEMANTIC_DRIFT_VALIDATION": ValidationEntry(
        key="SEMANTIC_DRIFT_VALIDATION",
        meaning="Verifica divergenza da MASTER o duplicazioni cross-modulo.",
        authority="PROMETEO_MASTER",
        master_refs=("MASTER-ANTIFRAG-001", "ARCH-BOUNDARY-001"),
        validates=("runtime_semantics", "registry_refs", "hardcoded_rules"),
        failure_mode="GOVERNANCE_ESCALATION",
        escalation_key="GOVERNANCE_ESCALATION",
    ),
}


def get_validation_entry(value: str) -> ValidationEntry:
    return VALIDATION_REGISTRY[normalize_key(value)]


def validation_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(VALIDATION_REGISTRY)
