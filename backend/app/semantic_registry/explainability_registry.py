from __future__ import annotations

from .contracts import ExplainabilityEntry, normalize_key, registry_to_dict


EXPLAINABILITY_REGISTRY_VERSION = "A1.5"

EXPLAINABILITY_REGISTRY: dict[str, ExplainabilityEntry] = {
    "CAUSAL_BASIS": ExplainabilityEntry(
        key="CAUSAL_BASIS",
        meaning="La decisione deve indicare la causa operativa che l'ha prodotta.",
        authority="PROMETEO_MASTER",
        master_refs=("STATION-CAUSALITY-001", "EVENT-CAUSALITY-001"),
        required_evidence=("evento", "postazione", "vincolo", "segnale planner"),
        sufficiency_rule="Almeno una causa operativa concreta deve essere visibile al TL.",
    ),
    "PROPAGATION_BASIS": ExplainabilityEntry(
        key="PROPAGATION_BASIS",
        meaning="La decisione deve mostrare come un vincolo si propaga su route, componenti o stazioni.",
        authority="PROMETEO_MASTER",
        master_refs=("CONSTRAINT-PROPAGATION-001", "COMPONENT-GRAPH-001"),
        required_evidence=("origine", "destinazione", "tipo propagazione"),
        sufficiency_rule="Ogni impatto indiretto deve dichiarare il collegamento usato.",
    ),
    "CONFIDENCE_BASIS": ExplainabilityEntry(
        key="CONFIDENCE_BASIS",
        meaning="La decisione deve dichiarare CERTO, INFERITO, DA_VERIFICARE o BLOCCATO quando influenza azione.",
        authority="PROMETEO_MASTER",
        master_refs=("CONFIDENCE-SEMANTICS-001",),
        required_evidence=("stato confidence", "fonte", "incertezza residua"),
        sufficiency_rule="Lo stato confidence deve essere compatibile con l'azione proposta.",
    ),
    "GOVERNANCE_BASIS": ExplainabilityEntry(
        key="GOVERNANCE_BASIS",
        meaning="La decisione deve rendere visibile il confine tra autonomia runtime e autorita TL.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-AUTHORITY-001", "AUTONOMIC-GOVERNANCE-001"),
        required_evidence=("autorita applicata", "limite runtime", "conferma richiesta"),
        sufficiency_rule="Ogni override o promozione deve citare l'autorita che la consente.",
    ),
    "ESCALATION_BASIS": ExplainabilityEntry(
        key="ESCALATION_BASIS",
        meaning="La decisione deve spiegare perche e stata escalata e quale conferma serve.",
        authority="PROMETEO_MASTER",
        master_refs=("STRATEGIC-HITL-001", "OPERATIONAL-RISK-001"),
        required_evidence=("trigger", "severity", "richiesta TL"),
        sufficiency_rule="Ogni escalation deve essere bounded, reversibile e motivata.",
    ),
    "UNCERTAINTY_BASIS": ExplainabilityEntry(
        key="UNCERTAINTY_BASIS",
        meaning="La decisione deve dichiarare dati mancanti o assunzioni non confermate.",
        authority="PROMETEO_MASTER",
        master_refs=("UNCERTAINTY-TRUST-001", "REASONING-BOUNDARY-001"),
        required_evidence=("dato mancante", "assunzione", "prossima verifica"),
        sufficiency_rule="Nessuna incertezza deve essere nascosta dietro un'azione operativa.",
    ),
    "OVERRIDE_BASIS": ExplainabilityEntry(
        key="OVERRIDE_BASIS",
        meaning="La decisione deve motivare ogni override e conservarne la reversibilita.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-OVERRIDE-001", "GOVERNANCE-MEMORY-001"),
        required_evidence=("autorita override", "motivo", "rollback"),
        sufficiency_rule="Override valido solo se auditabile e attribuito.",
    ),
    "STABILIZATION_BASIS": ExplainabilityEntry(
        key="STABILIZATION_BASIS",
        meaning="La decisione deve spiegare perche una semantica puo diventare stabile.",
        authority="PROMETEO_MASTER",
        master_refs=("COGNITIVE-STABILIZATION-001", "INSTITUTIONAL-STABILIZATION-001"),
        required_evidence=("fonte stabile", "assenza conflitti", "conferma"),
        sufficiency_rule="La stabilizzazione richiede fonte autorevole e assenza di contraddizioni aperte.",
    ),
}

MINIMUM_EXPLAINABILITY_KEYS = (
    "CAUSAL_BASIS",
    "CONFIDENCE_BASIS",
    "GOVERNANCE_BASIS",
    "UNCERTAINTY_BASIS",
)


def get_explainability_entry(value: str) -> ExplainabilityEntry:
    return EXPLAINABILITY_REGISTRY[normalize_key(value)]


def explainability_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(EXPLAINABILITY_REGISTRY)
