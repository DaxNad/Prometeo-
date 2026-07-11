from __future__ import annotations

import json

import pytest

from app.domain.article_operational_registry import (
    get_operational_registry_entry,
    reset_article_operational_registry_cache,
)
from app.services import intake_placement_execution_bridge as execution_bridge
from app.services.intake_destination_classifier import (
    ERROR_UNAUTHORIZED_AUTHORITY_ROLE,
)
from app.services.intake_placement_dry_run_service import (
    ERROR_CLASSIFICATION_NOT_READY,
    PlacementDryRunStatus,
)
from app.services.intake_single_item_orchestrator import IntakeOrchestrationStatus
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeStatus,
    process_structured_intake_payload,
)
from app.services.structured_intake_discrepancy_detector import (
    IntakeDiscrepancyStatus,
)


ARTICLE = "99877"


def test_lower_authority_unconfirmed_value_does_not_override_authoritative_registry(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    registry = {
        "version": "synthetic-discrepancy-test",
        "articles": {
            ARTICLE: {
                "article": ARTICLE,
                "operational_class": "STANDARD",
                "semantic_status": "CERTO",
                "planner_eligible": True,
                "tl_confirmation_required": False,
                "source": "human_operational_confirmation",
                "source_authority": "RESPONSABILE_PRODUZIONE",
            }
        },
    }
    registry_path.write_text(json.dumps(registry, sort_keys=True), encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    monkeypatch.setattr(
        execution_bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("authoritative writer called"),
    )
    reset_article_operational_registry_cache()

    try:
        registry_before = registry_path.read_bytes()
        authoritative_before = get_operational_registry_entry(ARTICLE)
        assert authoritative_before is not None
        assert authoritative_before["operational_class"] == "STANDARD"
        assert authoritative_before["semantic_status"] == "CERTO"

        source_id = f"preview:synthetic-discrepancy:{ARTICLE}"
        result = process_structured_intake_payload(
            {
                "field_name": "operational_class",
                "value": "NON_STANDARD",
                "source_id": source_id,
                "source_type": "spec_intake_preview",
                "source_status": "SOURCE_FOUND",
                "semantic_status": "DA_VERIFICARE",
                "authority_role": "OPERATORE",
                "context": {"article": ARTICLE},
                "metadata": {},
            }
        )

        assert result.status == StructuredIntakeFacadeStatus.NOT_EXECUTED
        assert result.writer_called is False
        assert result.error_code == ERROR_CLASSIFICATION_NOT_READY
        assert result.source_id == source_id

        adapter_item = result.adapter_result.item
        assert adapter_item is not None
        assert adapter_item.value == "NON_STANDARD"
        assert adapter_item.source_id == source_id
        assert adapter_item.source_type == "spec_intake_preview"
        assert adapter_item.source_status == "SOURCE_FOUND"
        assert adapter_item.semantic_status == "DA_VERIFICARE"
        assert adapter_item.authority_role == "OPERATORE"

        orchestration = result.orchestration_result
        assert orchestration is not None
        assert orchestration.status == IntakeOrchestrationStatus.NOT_EXECUTED
        assert orchestration.execution is None
        assert orchestration.writer_called is False
        assert orchestration.classification.error_code == ERROR_UNAUTHORIZED_AUTHORITY_ROLE
        assert orchestration.classification.requires_review is True
        assert orchestration.classification.source_id == source_id
        assert orchestration.classification.original_value == "NON_STANDARD"

        discrepancy = orchestration.discrepancy_result
        assert discrepancy is not None
        assert discrepancy.status == IntakeDiscrepancyStatus.DISCREPANCY_DETECTED
        assert discrepancy.comparison_performed is True
        assert discrepancy.discrepancy_detected is True
        assert discrepancy.authoritative_value == "STANDARD"
        assert discrepancy.incoming_value == "NON_STANDARD"
        assert discrepancy.authoritative_semantic_status == "CERTO"
        assert discrepancy.incoming_semantic_status == "DA_VERIFICARE"
        assert discrepancy.authoritative_source == "human_operational_confirmation"
        assert discrepancy.incoming_source_id == source_id
        assert discrepancy.requires_review is True
        assert discrepancy.persistence_allowed is False
        assert discrepancy.incoming_authority_role == "OPERATORE"

        plan = orchestration.plan
        assert plan is not None
        assert plan.status == PlacementDryRunStatus.INVALID_PLACEMENT_REQUEST
        assert plan.error_code == ERROR_CLASSIFICATION_NOT_READY
        assert plan.blocking_reasons == (ERROR_CLASSIFICATION_NOT_READY,)
        assert plan.ready_for_persistence is False
        assert plan.requires_review is True
        assert plan.source_id == source_id
        assert plan.source_status == "SOURCE_FOUND"
        assert plan.semantic_status == "DA_VERIFICARE"
        assert plan.authority_role == "OPERATORE"
        assert plan.target_repository is None
        assert plan.target_service is None

        assert registry_path.read_bytes() == registry_before
        authoritative_after = get_operational_registry_entry(ARTICLE)
        assert authoritative_after == authoritative_before
        assert authoritative_after["operational_class"] == "STANDARD"
        assert authoritative_after["semantic_status"] == "CERTO"
        assert sorted(path.name for path in tmp_path.iterdir()) == [
            "article_operational_registry.json"
        ]

        discrepancy_evidence = " ".join(
            (
                orchestration.classification.review_reason or "",
                plan.review_reason or "",
                *plan.blocking_reasons,
            )
        )
        assert all(
            token in discrepancy_evidence
            for token in (ARTICLE, "STANDARD", "NON_STANDARD")
        ), (
            "PROMETEO blocca l'input per autorità/classificazione, ma la structured "
            "intake non confronta il nuovo valore con il registry autorevole e non "
            "rende esplicita la discrepanza STANDARD vs NON_STANDARD."
        )
    finally:
        reset_article_operational_registry_cache()
