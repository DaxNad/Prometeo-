from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.domain.article_operational_registry import (
    reset_article_operational_registry_cache,
)
from app.main import app
from app.services.intake_destination_classifier import IntakeDestination
from app.services.intake_placement_dry_run_service import PlacementDryRunStatus
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeStatus,
    process_structured_intake_payload,
)


ARTICLE = "99876"
SOURCE_ID = "human:synthetic-intake:99876"


def test_structured_intake_persists_and_is_read_back_by_tl_chat(
    monkeypatch,
    tmp_path,
):
    registry_path = tmp_path / "article_operational_registry.json"
    registry_path.write_text(
        json.dumps({"version": "synthetic-e2e", "articles": {}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_PREVIEW_ROOT",
        tmp_path / "spec_intake_preview",
    )
    monkeypatch.setattr(
        tl_chat_api,
        "LIFECYCLE_REGISTRY",
        tmp_path / "article_lifecycle_registry.json",
    )
    reset_article_operational_registry_cache()

    source_evidence = {
        "source_id": SOURCE_ID,
        "source_type": "human_operational_confirmation",
        "source_status": "SOURCE_FOUND",
        "semantic_status": "CERTO",
    }
    audit_note = "Conferma umana sintetica per chiusura intake E2E."
    result = process_structured_intake_payload(
        {
            "field_name": "operational_class",
            "value": "STANDARD",
            **source_evidence,
            "authority_role": "RESPONSABILE_PRODUZIONE",
            "context": {
                "article": ARTICLE,
                "planner_eligible": True,
                "tl_confirmation_required": False,
            },
            "metadata": {
                "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
                "audit_note": audit_note,
                "confirmed_at": "2026-07-10T09:00:00+00:00",
                "description": "Articolo sintetico intake E2E",
            },
        },
        requested_by_role="RESPONSABILE_PRODUZIONE",
    )

    assert result.ok is True
    assert result.status == StructuredIntakeFacadeStatus.ORCHESTRATED
    assert result.source_id == SOURCE_ID
    assert result.orchestration_result is not None
    assert result.orchestration_result.classification.destination == IntakeDestination.HUMAN_CONFIRMATIONS
    assert result.orchestration_result.plan is not None
    assert result.orchestration_result.plan.status == PlacementDryRunStatus.READY
    assert result.orchestration_result.execution is not None
    assert result.orchestration_result.execution.persisted is True

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    record = stored["articles"][ARTICLE]
    assert record["source"] == "human_operational_confirmation"
    assert record["source_evidence"] == {
        **source_evidence,
        "matched_rules": [
            "STRUCTURED_HUMAN_CONFIRMATION",
        ],
    }
    assert record["audit_note"] == audit_note
    assert record["confirmation_origin"] == "HUMAN_EXPLICIT_CONFIRMATION"
    assert record["source_authority"] == "RESPONSABILE_PRODUZIONE"

    response = TestClient(app).post(
        "/tl/chat",
        json={
            "question": f"Posso assemblare il {ARTICLE}?",
            "context": {"article": ARTICLE},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith(
        f"Sì. L'articolo {ARTICLE} risulta appartenere alla produzione ordinaria."
    )
    assert body["confidence"] == "CERTO"
    assert body["requires_confirmation"] is False

    persisted_after_readback = json.loads(registry_path.read_text(encoding="utf-8"))
    assert persisted_after_readback == stored

    reset_article_operational_registry_cache()
