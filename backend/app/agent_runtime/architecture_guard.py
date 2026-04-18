from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ArchitectureCheckResult:

    status: str = "ALLOW"

    domain_coherence: bool = True
    modularity_preserved: bool = True
    explainability_preserved: bool = True

    duplication_risk: bool = False
    hardcode_risk: bool = False
    crud_drift_risk: bool = False

    planner_impact: bool = False
    registry_impact: bool = False

    requires_arch_review: bool = False

    notes: List[str] = None


def evaluate_architecture(change_context: Dict) -> ArchitectureCheckResult:

    result = ArchitectureCheckResult(notes=[])

    # dominio core
    if change_context.get("breaks_order_event_model"):

        result.domain_coherence = False
        result.requires_arch_review = True

        result.notes.append(
            "Order -> ProductionEvent semantic structure altered"
        )

        result.status = "REVIEW"

    # hardcode fragile
    if change_context.get("introduces_hardcode"):

        result.hardcode_risk = True

        result.notes.append(
            "hardcoded domain logic detected"
        )

        result.status = "REVIEW"

    # duplicazioni semantiche
    if change_context.get("duplicates_domain_logic"):

        result.duplication_risk = True

        result.notes.append(
            "duplicate semantic source across modules"
        )

        result.status = "REVIEW"

    # deriva CRUD
    if change_context.get("crud_drift"):

        result.crud_drift_risk = True
        result.requires_arch_review = True

        result.notes.append(
            "risk of degrading PROMETEO into CRUD system"
        )

        result.status = "REVIEW"

    # explainability planner
    if change_context.get("reduces_explainability"):

        result.explainability_preserved = False
        result.planner_impact = True

        result.notes.append(
            "planner decision explainability reduced"
        )

        result.status = "REVIEW"

    # registry dominio
    if change_context.get("changes_semantic_registry"):

        result.registry_impact = True
        result.requires_arch_review = True

        result.notes.append(
            "semantic registry modified"
        )

        result.status = "REVIEW"

    # planner logic
    if change_context.get("changes_planner_logic"):

        result.planner_impact = True

        result.notes.append(
            "planner logic modified"
        )

    return result


def summarize_guard_result(result: ArchitectureCheckResult) -> Dict:

    return {

        "status": result.status,

        "domain_ok": result.domain_coherence,
        "modularity_ok": result.modularity_preserved,
        "explainability_ok": result.explainability_preserved,

        "duplication_risk": result.duplication_risk,
        "hardcode_risk": result.hardcode_risk,
        "crud_drift_risk": result.crud_drift_risk,

        "planner_impact": result.planner_impact,
        "registry_impact": result.registry_impact,

        "requires_arch_review": result.requires_arch_review,

        "notes": result.notes or [],
    }

