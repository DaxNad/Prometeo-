import inspect

import pytest

from app.services import intake_single_item_orchestrator as orchestrator
from app.services.intake_destination_classifier import IntakeItem
from app.services.intake_placement_dry_run_service import PlacementDryRunStatus
from app.services.intake_placement_execution_bridge import (
    IntakePlacementExecutionResult,
    PlacementExecutionStatus,
)
from app.services.intake_single_item_orchestrator import (
    IntakeOrchestrationStatus,
    orchestrate_intake_item,
)


def _human_item(**overrides):
    payload = {
        "field_name": "operational_class",
        "value": "STANDARD",
        "source_id": "human:SYNTH01",
        "source_type": "human_operational_confirmation",
        "source_status": "SOURCE_FOUND",
        "semantic_status": "CERTO",
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "context": {
            "article": "SYNTH01",
            "planner_eligible": True,
            "tl_confirmation_required": False,
        },
        "metadata": {
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        },
    }
    payload.update(overrides)
    return IntakeItem(**payload)


def test_ready_plan_is_executed_once(monkeypatch):
    calls = []

    def execute(plan):
        calls.append(plan)
        return IntakePlacementExecutionResult(
            ok=True,
            status=PlacementExecutionStatus.EXECUTED,
            writer_called=True,
            source_id=plan.source_id,
            persisted=True,
            created=True,
        )

    monkeypatch.setattr(orchestrator, "execute_intake_placement", execute)

    result = orchestrate_intake_item(_human_item())

    assert len(calls) == 1
    assert result.status == IntakeOrchestrationStatus.EXECUTED
    assert result.classification.ok is True
    assert result.plan.status == PlacementDryRunStatus.READY
    assert result.execution is not None
    assert result.execution.status == PlacementExecutionStatus.EXECUTED
    assert result.writer_called is True


def test_non_ready_plan_does_not_execute(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "execute_intake_placement",
        lambda _plan: pytest.fail("execution bridge called"),
    )

    result = orchestrate_intake_item(
        IntakeItem(
            field_name="drawing",
            value="DRW-01",
            source_id="preview:SYNTH01",
            source_type="spec_intake_preview",
            source_status="PREVIEW_ONLY",
            semantic_status="DA_VERIFICARE",
            context={"article": "SYNTH01"},
        )
    )

    assert result.status == IntakeOrchestrationStatus.NOT_EXECUTED
    assert result.execution is None
    assert result.writer_called is False
    assert result.plan.status == PlacementDryRunStatus.REVIEW_REQUIRED


def test_unclassified_item_preserves_structured_results(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "execute_intake_placement",
        lambda _plan: pytest.fail("execution bridge called"),
    )

    result = orchestrate_intake_item(
        IntakeItem(
            field_name="note",
            value="nota descrittiva",
            source_id="source:SYNTH",
        )
    )

    assert result.status == IntakeOrchestrationStatus.NOT_EXECUTED
    assert result.classification.ok is True
    assert result.classification.destination is None
    assert result.classification.error_code == "UNCLASSIFIED"
    assert result.classification.requires_review is True
    assert result.plan.ready_for_persistence is False
    assert result.execution is None


def test_invalid_input_does_not_execute(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "execute_intake_placement",
        lambda _plan: pytest.fail("execution bridge called"),
    )

    result = orchestrate_intake_item(None)

    assert result.status == IntakeOrchestrationStatus.INVALID_INPUT
    assert result.execution is None
    assert result.writer_called is False


def test_orchestrator_has_no_batch_dynamic_dispatch_or_retry():
    source = inspect.getsource(orchestrator)

    assert "classify_intake_items" not in source
    assert "plan_intake_placements" not in source
    assert "getattr(" not in source
    assert "globals(" not in source
    assert "import_module" not in source
    assert "retry" not in source.lower()
    assert source.count("execute_intake_placement(") == 1


def test_orchestrator_does_not_hardcode_article_12514():
    assert "12514" not in inspect.getsource(orchestrator)
