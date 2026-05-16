from __future__ import annotations

from .contracts import ExecutionReadinessEntry, normalize_key, registry_to_dict


EXECUTION_READINESS_REGISTRY_VERSION = "A1.5"

EXECUTION_READINESS_REGISTRY: dict[str, ExecutionReadinessEntry] = {
    "READY_FOR_PREVIEW": ExecutionReadinessEntry(
        key="READY_FOR_PREVIEW",
        meaning="Semantica sufficiente per mostrare preview o suggerimento TL-safe.",
        authority="PROMETEO_MASTER",
        master_refs=("TL-CONTRACT-001", "AI-GOVERNANCE-001"),
        required_states=("INFERITO", "DA_VERIFICARE"),
        blocking_states=("BLOCCATO",),
        readiness_rule="Ammesso se output resta non-scrivente, marcato come preview e spiegabile.",
    ),
    "READY_FOR_PLANNER_CONSIDERATION": ExecutionReadinessEntry(
        key="READY_FOR_PLANNER_CONSIDERATION",
        meaning="Semantica sufficiente per entrare nel set considerabile dal planner.",
        authority="PROMETEO_MASTER",
        master_refs=("PLANNER-BOUNDARY-001",),
        required_states=("STANDARD", "CERTO"),
        blocking_states=("DA_VERIFICARE", "BLOCCATO", "REFERENCE_ONLY"),
        readiness_rule="Richiede gate planner completo e domanda operativa attiva.",
    ),
    "READY_FOR_EXECUTION": ExecutionReadinessEntry(
        key="READY_FOR_EXECUTION",
        meaning="Semantica sufficiente per azione operativa non ambigua.",
        authority="PROMETEO_MASTER",
        master_refs=("EXECUTOR-GATE-001", "TL-AUTHORITY-001"),
        required_states=("CERTO",),
        blocking_states=("INFERITO", "DA_VERIFICARE", "BLOCCATO", "REFERENCE_ONLY"),
        readiness_rule="Richiede fonte certa, gate superati, nessun blocker e conferma dove necessaria.",
    ),
    "READY_FOR_STABILIZATION": ExecutionReadinessEntry(
        key="READY_FOR_STABILIZATION",
        meaning="Semantica sufficiente per diventare riferimento stabile di dominio.",
        authority="PROMETEO_MASTER",
        master_refs=("COGNITIVE-STABILIZATION-001", "MASTER-ANTIFRAG-001"),
        required_states=("CERTO",),
        blocking_states=("INFERITO", "DA_VERIFICARE", "BLOCCATO"),
        readiness_rule="Richiede autorita, tracciabilita, assenza conflitti e rollback governance.",
    ),
}


def get_execution_readiness_entry(value: str) -> ExecutionReadinessEntry:
    return EXECUTION_READINESS_REGISTRY[normalize_key(value)]


def execution_readiness_registry_as_dict() -> dict[str, dict]:
    return registry_to_dict(EXECUTION_READINESS_REGISTRY)
