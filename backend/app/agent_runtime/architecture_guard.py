"""
ARCHITECTURE_GUARD v0

Verifica coerenza delle modifiche rispetto a:
PROMETEO_MANIFESTO_v1

NON blocca il runtime.
Fornisce solo segnalazione semantica.
"""

from dataclasses import dataclass
from typing import List, Literal, Dict

StatusType = Literal["OK", "WARNING", "REVIEW"]


@dataclass
class ArchitectureCheckResult:
    domain_coherence: bool = True
    modularity_preserved: bool = True
    explainability_preserved: bool = True
    duplication_risk: bool = False
    hardcode_risk: bool = False
    notes: List[str] = None
    status: StatusType = "OK"


def evaluate_architecture_guard(change_context: Dict) -> ArchitectureCheckResult:

    result = ArchitectureCheckResult(notes=[])

    if change_context.get("hardcoded_values"):
        result.hardcode_risk = True
        result.notes.append("hardcoded values detected")
        result.status = "WARNING"

    if change_context.get("duplicate_logic"):
        result.duplication_risk = True
        result.notes.append("duplicate logic risk")
        result.status = "REVIEW"

    if change_context.get("opaque_decision_logic"):
        result.explainability_preserved = False
        result.notes.append("decision logic not explainable")
        result.status = "REVIEW"

    if change_context.get("breaks_order_event_model"):
        result.domain_coherence = False
        result.notes.append("order-event semantic structure altered")
        result.status = "REVIEW"

    return result


def summarize_guard_result(result: ArchitectureCheckResult) -> Dict:
    return {
        "status": result.status,
        "domain_ok": result.domain_coherence,
        "modularity_ok": result.modularity_preserved,
        "explainability_ok": result.explainability_preserved,
        "duplication_risk": result.duplication_risk,
        "hardcode_risk": result.hardcode_risk,
        "notes": result.notes or [],
    }
