from __future__ import annotations

from .contracts import SemanticGateEntry, normalize_key, registry_to_dict


SEMANTIC_GATE_REGISTRY_VERSION = "A1.5"

SEMANTIC_GATE_REGISTRY: dict[str, SemanticGateEntry] = {
    "PLANNER_ADMISSION_GATE": SemanticGateEntry(
        key="PLANNER_ADMISSION_GATE",
        meaning="Gate semantico per ammissione a pianificazione ordinaria.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BOUNDARY-001", "PLANNER-BLOCKING-001"),
        inputs=("operational_class", "route_status", "confidence", "active_demand", "blocking_constraint"),
        pass_rule="STANDARD, route CERTO, confidence CERTO, domanda attiva e nessun blocker.",
        fail_rule="Qualsiasi incertezza o blocker produce non-ammissione e spiegazione dei motivi.",
    ),
    "TL_CONFIRMATION_GATE": SemanticGateEntry(
        key="TL_CONFIRMATION_GATE",
        meaning="Gate per promozione da inferito o riferimento a uso operativo.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-AUTHORITY-001", "TL-CONTRACT-001"),
        inputs=("confidence", "operational_class", "requested_action", "tl_confirmation"),
        pass_rule="Conferma TL esplicita o fonte reale autorevole.",
        fail_rule="Restare in preview, riferimento o DA_VERIFICARE.",
    ),
    "EXPLAINABILITY_GATE": SemanticGateEntry(
        key="EXPLAINABILITY_GATE",
        meaning="Gate minimo per decisioni planner, ATLAS o runtime stabilizzabili.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-EXPLAINABILITY-001", "AUTONOMIC-EXPLAINABILITY-001"),
        inputs=("causal_basis", "confidence_basis", "governance_basis", "uncertainty_basis"),
        pass_rule="Motivazioni minime presenti e compatibili con l'azione.",
        fail_rule="Escalation explainability e blocco stabilizzazione.",
    ),
    "GOVERNANCE_GATE": SemanticGateEntry(
        key="GOVERNANCE_GATE",
        meaning="Gate per impedire drift architetturale, duplicazioni e CRUD drift.",
        authority="PROMETEO_MASTER",
        master_refs=("ARCH-BOUNDARY-001", "GUARD-OBSERVABILITY-001"),
        inputs=("domain_coherence", "modularity", "registry_impact", "planner_impact"),
        pass_rule="Coerenza dominio preservata e impatti dichiarati.",
        fail_rule="Review architetturale richiesta.",
    ),
}


def get_semantic_gate_entry(value: str) -> SemanticGateEntry:
    return SEMANTIC_GATE_REGISTRY[normalize_key(value)]


def semantic_gate_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(SEMANTIC_GATE_REGISTRY)
