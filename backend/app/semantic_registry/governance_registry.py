from __future__ import annotations

from .contracts import AuthorityBoundary, GovernanceEntry, normalize_key, registry_to_dict


GOVERNANCE_REGISTRY_VERSION = "A1.5"

AUTHORITY_PRECEDENCE = (
    AuthorityBoundary("REAL_SPEC", 1, "SOURCE OF TRUTH POLICY", "Verita produttiva documentale."),
    AuthorityBoundary("TL_CONFIRMATION", 2, "TL-AUTHORITY-001", "Autorita operativa finale."),
    AuthorityBoundary("PROMETEO_MASTER", 3, "MASTER-ANTIFRAG-001", "Autorita semantica primaria."),
    AuthorityBoundary("DOMAIN_STRUCTURE", 4, "DOMAIN-CHAIN-001", "Modello Order -> ProductionEvent -> Station/Phase."),
    AuthorityBoundary("RUNTIME_PREPARATION", 5, "AI-GOVERNANCE-001", "Supporto runtime non autoritativo."),
)

GOVERNANCE_REGISTRY: dict[str, GovernanceEntry] = {
    "TL_SUPREMACY": GovernanceEntry(
        key="TL_SUPREMACY",
        meaning="Il TL resta autorita operativa finale su conferme, override e promozioni.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-AUTHORITY-001", "TL-OVERRIDE-001"),
        precedence=2,
        admissibility_rule="Runtime puo suggerire, ma non stabilizzare contro conferma TL.",
        rollback_rule="Ogni override TL deve essere auditabile e reversibile.",
    ),
    "BOUNDED_AUTONOMY": GovernanceEntry(
        key="BOUNDED_AUTONOMY",
        meaning="AI, ATLAS ed executor operano entro confini espliciti e spiegabili.",
        authority="PROMETEO_MASTER",
        master_refs=("AI-GOVERNANCE-001", "EXECUTOR-GATE-001"),
        precedence=5,
        admissibility_rule="Autonomia ammessa solo per monitoraggio, preview e suggerimenti gated.",
        rollback_rule="Nessuna scrittura operativa irreversibile senza gate e conferma.",
    ),
    "SEMANTIC_AUTHORITY_PRECEDENCE": GovernanceEntry(
        key="SEMANTIC_AUTHORITY_PRECEDENCE",
        meaning="Fonti reali e TL precedono MASTER, struttura dominio e inferenze runtime.",
        authority="PROMETEO_MASTER",
        master_refs=("MASTER-ANTIFRAG-001",),
        precedence=1,
        admissibility_rule="In conflitto vince la fonte con precedence_rank piu basso.",
        rollback_rule="Semantiche derivate da fonte inferiore vanno declassate o ritirate.",
    ),
    "GOVERNANCE_ROLLBACK": GovernanceEntry(
        key="GOVERNANCE_ROLLBACK",
        meaning="Ogni promozione, override o stabilizzazione deve poter essere invertita.",
        authority="PROMETEO_MASTER",
        master_refs=("RECOVERY-STABILIZATION-001", "GOVERNANCE-MEMORY-001"),
        precedence=3,
        admissibility_rule="Promozione ammessa solo con fonte, motivazione e stato precedente.",
        rollback_rule="Conservare rollback_id, causa o vincolo che consente ritorno allo stato precedente.",
    ),
    "CONTRADICTION_HANDLING": GovernanceEntry(
        key="CONTRADICTION_HANDLING",
        meaning="Contraddizioni tra moduli o fonti non vengono risolte con euristiche opache.",
        authority="PROMETEO_MASTER",
        master_refs=("COGNITIVE-INTEGRITY-001", "MASTER-ANTIFRAG-001"),
        precedence=3,
        admissibility_rule="Contraddizione aperta blocca stabilizzazione e richiede escalation.",
        rollback_rule="La semantica meno autorevole resta sospesa fino a risoluzione.",
    ),
    "GOVERNANCE_ADMISSIBILITY": GovernanceEntry(
        key="GOVERNANCE_ADMISSIBILITY",
        meaning="Una decisione e ammissibile solo se dominio, explainability, confidence e gate sono coerenti.",
        authority="PROMETEO_MASTER",
        master_refs=("GUARD-OBSERVABILITY-001", "PLANNER-EXPLAINABILITY-001"),
        precedence=3,
        admissibility_rule="Gate fallito o spiegazione insufficiente impediscono stabilizzazione.",
        rollback_rule="Ripristinare stato pre-decisione se un gate viene invalidato.",
    ),
}


def get_governance_entry(value: str) -> GovernanceEntry:
    return GOVERNANCE_REGISTRY[normalize_key(value)]


def governance_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(GOVERNANCE_REGISTRY)
