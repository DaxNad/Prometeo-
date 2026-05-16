from __future__ import annotations

from .contracts import ConfidenceEntry, normalize_key, registry_to_dict


CONFIDENCE_REGISTRY_VERSION = "A1.5"

CONFIDENCE_REGISTRY: dict[str, ConfidenceEntry] = {
    "CERTO": ConfidenceEntry(
        key="CERTO",
        meaning="Semantica confermata da fonte reale, TL o struttura dominio autorevole.",
        authority="PROMETEO_MASTER",
        master_refs=("CONFIDENCE-SEMANTICS-001", "TL-AUTHORITY-001"),
        escalation_behavior="Nessuna escalation ordinaria; escalation solo se emerge contraddizione nuova.",
        execution_admissibility="Ammissibile solo se anche route, classe operativa, domanda e vincoli sono coerenti.",
        obligations=(
            "indicare fonte confermante",
            "non promuovere inferenze derivate oltre la fonte",
        ),
        validation_requirements=(
            "fonte autorevole presente",
            "assenza di contraddizioni aperte",
        ),
        hitl_requirements=("TL necessario solo per override o conflitti successivi",),
        rollback_constraints=("rollback richiesto se la fonte confermata viene invalidata",),
    ),
    "INFERITO": ConfidenceEntry(
        key="INFERITO",
        meaning="Semantica dedotta da segnali coerenti ma non ancora confermata come verita operativa.",
        authority="PROMETEO_MASTER",
        master_refs=("CONFIDENCE-SEMANTICS-001", "REASONING-BOUNDARY-001"),
        escalation_behavior="Soft escalation verso verifica TL quando impatta staging, planner o decisioni operative.",
        execution_admissibility="Non promuove esecuzione automatica; puo alimentare preview e spiegazioni.",
        obligations=(
            "esplicitare base causale dell'inferenza",
            "marcare l'incertezza residua",
        ),
        validation_requirements=(
            "segnali sorgente tracciati",
            "nessuna fonte CERTO contraria",
        ),
        hitl_requirements=("conferma TL prima di stabilizzazione o staging operativo",),
        rollback_constraints=("inferenza reversibile senza perdita della fonte originaria",),
    ),
    "DA_VERIFICARE": ConfidenceEntry(
        key="DA_VERIFICARE",
        meaning="Semantica incompleta, non verificata o non risolta.",
        authority="PROMETEO_MASTER",
        master_refs=("CONFIDENCE-SEMANTICS-001", "STRATEGIC-HITL-001"),
        escalation_behavior="Escalation TL richiesta quando la semantica entra in un flusso operativo.",
        execution_admissibility="Blocca decisioni automatiche e pianificazione piena.",
        obligations=(
            "indicare quali dati mancano",
            "proporre verifica TL o fonte reale necessaria",
        ),
        validation_requirements=("campo o fonte mancante esplicitata",),
        hitl_requirements=("conferma TL obbligatoria per promozione semantica",),
        rollback_constraints=("nessuna promozione persistente senza evento o fonte di conferma",),
    ),
    "BLOCCATO": ConfidenceEntry(
        key="BLOCCATO",
        meaning="Semantica o vincolo che impedisce avanzamento operativo sicuro.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BLOCKING-001", "EVENT-CAUSALITY-001"),
        escalation_behavior="Escalation bloccante con causa, vincolo e proprietario di sblocco.",
        execution_admissibility="Non ammissibile a esecuzione finche il vincolo resta aperto.",
        obligations=(
            "esplicitare vincolo bloccante",
            "indicare conflitti evitati",
        ),
        validation_requirements=(
            "vincolo bloccante identificato",
            "stato di risoluzione tracciabile",
        ),
        hitl_requirements=("TL richiesto per sblocco, override o riclassificazione",),
        rollback_constraints=("override deve produrre rollback_id o motivazione reversibile",),
    ),
    "STANDARD": ConfidenceEntry(
        key="STANDARD",
        meaning="Classe operativa ordinaria, non sinonimo di certezza assoluta.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BOUNDARY-001", "CONFIDENCE-SEMANTICS-001"),
        escalation_behavior="Escalation solo se route, confidence o domanda rendono il profilo non ammissibile.",
        execution_admissibility="Candidato al planner solo con confidence CERTO, route CERTO, domanda attiva e nessun blocker.",
        obligations=("non confondere classe operativa con stato confidence",),
        validation_requirements=("classe normalizzata", "gate planner separato dalla classe"),
        hitl_requirements=("TL richiesto per eccezioni operative",),
        rollback_constraints=("declassamento consentito se emergono vincoli o contraddizioni",),
    ),
    "REFERENCE_ONLY": ConfidenceEntry(
        key="REFERENCE_ONLY",
        meaning="Articolo conosciuto come riferimento, non automaticamente pianificabile.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BOUNDARY-001", "TL-CONTRACT-001"),
        escalation_behavior="Soft escalation se qualcuno tenta promozione operativa senza ordine o conferma TL.",
        execution_admissibility="Non ammissibile a planner automatico senza ordine cliente attivo o conferma TL.",
        obligations=("esplicitare che la conoscenza e di riferimento",),
        validation_requirements=("non trattare come STANDARD per default",),
        hitl_requirements=("conferma TL richiesta per promozione operativa",),
        rollback_constraints=("promozione reversibile e auditabile",),
        aliases=("REFERENCE", "SOLO_RIFERIMENTO"),
    ),
}


def get_confidence_entry(value: str) -> ConfidenceEntry:
    key = normalize_key(value)
    for entry in CONFIDENCE_REGISTRY.values():
        if key == entry.key or key in entry.aliases:
            return entry
    return CONFIDENCE_REGISTRY["DA_VERIFICARE"]


def confidence_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(CONFIDENCE_REGISTRY)
