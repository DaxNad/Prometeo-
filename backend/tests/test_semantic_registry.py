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
    resolve_semantic_confidence,
    resolve_semantic_gate,
    semantic_accessor_boundaries,
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


def test_semantic_accessor_resolves_certo_confidence():
    result = resolve_semantic_confidence("CERTO")

    assert result["registry"] == "confidence_registry"
    assert result["normalized_key"] == "CERTO"
    assert result["fallback_applied"] is False
    assert result["read_only"] is True
    assert result["no_runtime_mutation"] is True
    assert result["entry"]["key"] == "CERTO"


def test_semantic_accessor_normalizes_reference_only_alias():
    result = resolve_semantic_confidence("solo-riferimento")

    assert result["normalized_key"] == "REFERENCE_ONLY"
    assert result["fallback_applied"] is True
    assert result["entry"]["key"] == "REFERENCE_ONLY"


def test_semantic_accessor_unknown_confidence_falls_back_to_da_verificare():
    result = resolve_semantic_confidence("NON_CANONICO")

    assert result["normalized_key"] == "DA_VERIFICARE"
    assert result["fallback_applied"] is True
    assert result["entry"]["key"] == "DA_VERIFICARE"


def test_semantic_accessor_resolves_planner_admission_gate():
    result = resolve_semantic_gate("PLANNER_ADMISSION_GATE")

    assert result["registry"] == "semantic_gate_registry"
    assert result["normalized_key"] == "PLANNER_ADMISSION_GATE"
    assert result["fallback_applied"] is False
    assert result["read_only"] is True
    assert result["no_runtime_mutation"] is True
    assert result["entry"]["key"] == "PLANNER_ADMISSION_GATE"


def test_semantic_accessor_unknown_gate_returns_read_only_fallback():
    result = resolve_semantic_gate("UNKNOWN_GATE")

    assert result["registry"] == "semantic_gate_registry"
    assert result["normalized_key"] == "UNKNOWN_GATE"
    assert result["fallback_applied"] is True
    assert result["read_only"] is True
    assert result["no_runtime_mutation"] is True
    assert result["admitted"] is False
    assert result["entry"] is None


def test_semantic_accessor_boundaries_are_read_only():
    boundaries = semantic_accessor_boundaries()

    assert boundaries["read_only"] is True
    assert boundaries["no_runtime_mutation"] is True
    assert boundaries["no_planner_behavior_change"] is True
    assert boundaries["no_execution_authority"] is True
    assert boundaries["confidence_fallback"] == "DA_VERIFICARE"


def test_semantic_accessor_diagnostics_read_all_canonical_confidence_states():
    for confidence in (
        "CERTO",
        "INFERITO",
        "DA_VERIFICARE",
        "BLOCCATO",
        "STANDARD",
        "REFERENCE_ONLY",
    ):
        result = resolve_semantic_confidence(confidence)

        assert result["normalized_key"] == confidence
        assert result["read_only"] is True
        assert result["no_runtime_mutation"] is True
        assert result["entry"]["key"] == confidence


def test_semantic_accessor_diagnostics_read_required_gates():
    for gate_key in ("PLANNER_ADMISSION_GATE", "TL_CONFIRMATION_GATE"):
        result = resolve_semantic_gate(gate_key)

        assert result["normalized_key"] == gate_key
        assert result["fallback_applied"] is False
        assert result["read_only"] is True
        assert result["no_runtime_mutation"] is True
        assert result["entry"]["key"] == gate_key


def test_semantic_accessor_diagnostics_keep_fallbacks_conservative():
    confidence = resolve_semantic_confidence("UNKNOWN_CONFIDENCE")
    gate = resolve_semantic_gate("UNKNOWN_GATE")

    assert confidence["normalized_key"] == "DA_VERIFICARE"
    assert confidence["fallback_applied"] is True
    assert confidence["read_only"] is True
    assert confidence["no_runtime_mutation"] is True

    assert gate["normalized_key"] == "UNKNOWN_GATE"
    assert gate["fallback_applied"] is True
    assert gate["admitted"] is False
    assert gate["read_only"] is True
    assert gate["no_runtime_mutation"] is True


def test_semantic_accessor_diagnostics_boundaries_block_runtime_authority():
    boundaries = semantic_accessor_boundaries()

    assert boundaries["read_only"] is True
    assert boundaries["no_runtime_mutation"] is True
    assert boundaries["no_planner_behavior_change"] is True
    assert boundaries["no_execution_authority"] is True
