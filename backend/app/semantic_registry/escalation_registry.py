from __future__ import annotations

from .contracts import EscalationEntry, normalize_key, registry_to_dict


ESCALATION_REGISTRY_VERSION = "A1.5"

ESCALATION_REGISTRY: dict[str, EscalationEntry] = {
    "SOFT_ESCALATION": EscalationEntry(
        key="SOFT_ESCALATION",
        meaning="Verifica richiesta senza blocco immediato del flusso informativo.",
        authority="PROMETEO_MASTER",
        master_refs=("STRATEGIC-HITL-001", "UNCERTAINTY-TRUST-001"),
        triggers=("INFERITO in contesto operativo", "warning validazione", "anomalia non bloccante"),
        severity="medium",
        requires_tl_confirmation=True,
        blocks_execution=False,
        obligations=("motivare incertezza", "indicare verifica richiesta"),
    ),
    "BLOCKING_ESCALATION": EscalationEntry(
        key="BLOCKING_ESCALATION",
        meaning="Escalation che impedisce esecuzione o promozione fino a risoluzione.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BLOCKING-001", "EVENT-CAUSALITY-001"),
        triggers=("BLOCCATO", "blocking_constraint", "route_empty", "unknown_route_stations"),
        severity="critical",
        requires_tl_confirmation=True,
        blocks_execution=True,
        obligations=("registrare vincolo", "esplicitare condizione di sblocco"),
    ),
    "GOVERNANCE_ESCALATION": EscalationEntry(
        key="GOVERNANCE_ESCALATION",
        meaning="Escalation su rischio architetturale, registry drift o confine di autonomia.",
        authority="PROMETEO_MASTER",
        master_refs=("ARCH-BOUNDARY-001", "MASTER-ANTIFRAG-001"),
        triggers=("changes_semantic_registry", "duplicates_domain_logic", "crud_drift", "reduces_explainability"),
        severity="high",
        requires_tl_confirmation=True,
        blocks_execution=True,
        obligations=("richiedere review architetturale", "citare regola violata"),
    ),
    "CONTRADICTION_ESCALATION": EscalationEntry(
        key="CONTRADICTION_ESCALATION",
        meaning="Escalation quando due fonti o moduli producono semantiche incompatibili.",
        authority="PROMETEO_MASTER",
        master_refs=("MASTER-ANTIFRAG-001", "COGNITIVE-INTEGRITY-001"),
        triggers=("fonte CERTO contraria", "moduli in disaccordo", "planner conflict"),
        severity="high",
        requires_tl_confirmation=True,
        blocks_execution=True,
        obligations=("preservare entrambe le evidenze", "non scegliere euristicamente senza autorita"),
    ),
    "EXPLAINABILITY_ESCALATION": EscalationEntry(
        key="EXPLAINABILITY_ESCALATION",
        meaning="Escalation quando una decisione non soddisfa il minimo spiegabile.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-EXPLAINABILITY-001", "AUTONOMIC-EXPLAINABILITY-001"),
        triggers=("spiegazione assente", "vincoli non citati", "priorita non motivata"),
        severity="high",
        requires_tl_confirmation=True,
        blocks_execution=True,
        obligations=("bloccare stabilizzazione", "richiedere motivazioni causali minime"),
    ),
}


def get_escalation_entry(value: str) -> EscalationEntry:
    return ESCALATION_REGISTRY.get(normalize_key(value), ESCALATION_REGISTRY["SOFT_ESCALATION"])


def escalation_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(ESCALATION_REGISTRY)
