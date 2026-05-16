from app.semantic_registry import (
    AUTHORITY_PRECEDENCE,
    CONFIDENCE_REGISTRY,
    ESCALATION_REGISTRY,
    EXECUTION_READINESS_REGISTRY,
    EXPLAINABILITY_REGISTRY,
    GOVERNANCE_REGISTRY,
    RUNTIME_SEMANTIC_AUDIT,
    SEMANTIC_GATE_REGISTRY,
    VALIDATION_REGISTRY,
    get_confidence_entry,
    registry_lookup_boundaries,
    resolve_confidence,
)


def test_confidence_registry_contains_master_canonical_states():
    assert set(CONFIDENCE_REGISTRY) == {
        "CERTO",
        "INFERITO",
        "DA_VERIFICARE",
        "BLOCCATO",
        "STANDARD",
        "REFERENCE_ONLY",
    }

    for entry in CONFIDENCE_REGISTRY.values():
        assert entry.authority == "PROMETEO_MASTER"
        assert entry.master_refs
        assert entry.escalation_behavior
        assert entry.execution_admissibility
        assert entry.validation_requirements
        assert entry.hitl_requirements
        assert entry.rollback_constraints


def test_confidence_resolution_is_conservative_for_unknown_values():
    entry = get_confidence_entry("unknown")
    resolution = resolve_confidence("unknown")

    assert entry.key == "DA_VERIFICARE"
    assert resolution.normalized_key == "DA_VERIFICARE"
    assert resolution.fallback_applied is True
    assert "fallback" in resolution.fallback_behavior
    assert resolution.payload["key"] == "DA_VERIFICARE"


def test_reference_only_aliases_are_normalized_without_promoting_execution():
    entry = get_confidence_entry("solo-riferimento")

    assert entry.key == "REFERENCE_ONLY"
    assert "Non ammissibile" in entry.execution_admissibility
    assert "conferma TL" in " ".join(entry.hitl_requirements)


def test_governance_authority_precedence_matches_master_policy():
    ranks = {boundary.authority: boundary.precedence_rank for boundary in AUTHORITY_PRECEDENCE}

    assert ranks["REAL_SPEC"] < ranks["TL_CONFIRMATION"] < ranks["PROMETEO_MASTER"]
    assert ranks["PROMETEO_MASTER"] < ranks["DOMAIN_STRUCTURE"] < ranks["RUNTIME_PREPARATION"]
    assert GOVERNANCE_REGISTRY["TL_SUPREMACY"].precedence == ranks["TL_CONFIRMATION"]


def test_registry_architecture_is_queryable_and_bounded():
    boundaries = registry_lookup_boundaries()

    assert boundaries["version"] == "A1.5"
    assert "runtime execution rewiring" in boundaries["lookup_boundaries"]["not_implemented_now"]
    assert "PLANNER_ADMISSION_GATE" in boundaries["prepared_registries"]["semantic_gates"]
    assert "READY_FOR_EXECUTION" in boundaries["prepared_registries"]["execution_readiness"]


def test_phase_a15_registries_cover_expected_semantic_domains():
    assert "BLOCKING_ESCALATION" in ESCALATION_REGISTRY
    assert "CONTRADICTION_ESCALATION" in ESCALATION_REGISTRY
    assert "CAUSAL_BASIS" in EXPLAINABILITY_REGISTRY
    assert "GOVERNANCE_BASIS" in EXPLAINABILITY_REGISTRY
    assert "SEMANTIC_CONSISTENCY_VALIDATION" in VALIDATION_REGISTRY
    assert "SEMANTIC_DRIFT_VALIDATION" in VALIDATION_REGISTRY
    assert "EXPLAINABILITY_GATE" in SEMANTIC_GATE_REGISTRY
    assert "READY_FOR_STABILIZATION" in EXECUTION_READINESS_REGISTRY


def test_runtime_semantic_audit_classifies_dispersion():
    classifications = {finding.classification for finding in RUNTIME_SEMANTIC_AUDIT}
    audited_areas = {finding.area for finding in RUNTIME_SEMANTIC_AUDIT}

    assert {"CANONICAL", "DUPLICATED", "PARTIAL", "HARD_CODED"}.issubset(classifications)
    assert "backend/app/api/tl_chat.py" in audited_areas
    assert "backend/app/agent_runtime/decision_engine.py" in audited_areas
    assert all(finding.extraction_target for finding in RUNTIME_SEMANTIC_AUDIT)
