from __future__ import annotations

from dataclasses import replace
import inspect

import pytest

from app.services import intake_placement_execution_bridge as bridge
from app.services.article_operational_confirmation_service import (
    ArticleOperationalConfirmationResult,
    ERROR_WRITE_SUCCEEDED_READBACK_FAILED,
)
from app.services.intake_destination_classifier import (
    IntakeDestination,
    IntakeItem,
    classify_intake_destination,
)
from app.services.intake_placement_dry_run_service import (
    IntakePlacementDryRunRequest,
    PlacementDryRunStatus,
    PlacementOperation,
    plan_intake_placement,
)
from app.services.intake_placement_execution_bridge import (
    ERROR_INVALID_EXECUTION_REQUEST,
    ERROR_INVALID_PAYLOAD,
    ERROR_INVALID_SOURCE_EVIDENCE,
    ERROR_INVALID_WRITER_ARGUMENTS,
    ERROR_PLAN_NOT_READY,
    ERROR_UNAUTHORIZED_DESTINATION,
    ERROR_UNAUTHORIZED_OPERATION,
    ERROR_UNAUTHORIZED_REPOSITORY,
    ERROR_UNAUTHORIZED_SECTION,
    ERROR_UNAUTHORIZED_SERVICE,
    PlacementExecutionStatus,
    execute_intake_placement,
)


def _human_plan():
    item = IntakeItem(
        field_name="operational_class",
        value="STANDARD",
        source_id="human:SYNTH01",
        source_type="human_operational_confirmation",
        source_status="SOURCE_FOUND",
        semantic_status="CERTO",
        authority_role="RESPONSABILE_PRODUZIONE",
        context={
            "article": "SYNTH01",
            "planner_eligible": True,
            "tl_confirmation_required": False,
        },
        metadata={
            "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
            "audit_note": "Conferma operativa esplicita.",
        },
    )
    classification = classify_intake_destination(item)
    return plan_intake_placement(
        IntakePlacementDryRunRequest(
            item=item,
            classification=classification,
        )
    )


def _writer_result(**overrides):
    payload = {
        "ok": True,
        "article": "SYNTH01",
        "created": True,
        "updated": False,
        "current_record": {"operational_class": "STANDARD"},
        "registry_path": "/tmp/article_operational_registry.json",
        "confirmed_at": "2026-07-08T10:00:00+00:00",
        "persisted": True,
    }
    payload.update(overrides)
    return ArticleOperationalConfirmationResult(**payload)


def test_ready_human_confirmation_calls_writer_once(monkeypatch):
    plan = _human_plan()
    calls = []

    def writer(**kwargs):
        calls.append(kwargs)
        return _writer_result()

    monkeypatch.setattr(bridge, "confirm_article_operational_status", writer)

    result = execute_intake_placement(plan)

    assert len(calls) == 1
    assert calls[0] == {
        **dict(plan.payload_preview["writer_arguments"]),
        "source_evidence": dict(plan.payload_preview["source_evidence"]),
    }
    assert result.ok is True
    assert result.status == PlacementExecutionStatus.EXECUTED
    assert result.writer_called is True
    assert result.persisted is True
    assert result.created is True
    assert result.updated is False
    assert result.writer_result is not None
    assert result.source_id == "human:SYNTH01"
    assert result.source_evidence == dict(plan.payload_preview["source_evidence"])


def test_writer_failure_is_returned_without_retry(monkeypatch):
    plan = _human_plan()
    calls = 0

    def writer(**_kwargs):
        nonlocal calls
        calls += 1
        return _writer_result(
            ok=False,
            created=False,
            persisted=True,
            error_code=ERROR_WRITE_SUCCEEDED_READBACK_FAILED,
        )

    monkeypatch.setattr(bridge, "confirm_article_operational_status", writer)

    result = execute_intake_placement(plan)

    assert calls == 1
    assert result.ok is False
    assert result.status == PlacementExecutionStatus.WRITER_FAILED
    assert result.writer_called is True
    assert result.persisted is True
    assert result.error_code == ERROR_WRITE_SUCCEEDED_READBACK_FAILED


@pytest.mark.parametrize(
    ("plan", "error_code"),
    [
        (None, ERROR_INVALID_EXECUTION_REQUEST),
        (
            replace(
                _human_plan(),
                status=PlacementDryRunStatus.REVIEW_REQUIRED,
                ok=False,
                ready_for_persistence=False,
                requires_review=True,
            ),
            ERROR_PLAN_NOT_READY,
        ),
        (
            replace(_human_plan(), destination=IntakeDestination.ARTICLE),
            ERROR_UNAUTHORIZED_DESTINATION,
        ),
        (
            replace(_human_plan(), operation=PlacementOperation.UPDATE),
            ERROR_UNAUTHORIZED_OPERATION,
        ),
        (
            replace(_human_plan(), target_repository="other_repository"),
            ERROR_UNAUTHORIZED_REPOSITORY,
        ),
        (
            replace(_human_plan(), target_service="other_service"),
            ERROR_UNAUTHORIZED_SERVICE,
        ),
        (
            replace(_human_plan(), target_section="other_section"),
            ERROR_UNAUTHORIZED_SECTION,
        ),
    ],
)
def test_rejected_plans_do_not_call_writer(monkeypatch, plan, error_code):
    def fail(**_kwargs):
        raise AssertionError("writer called")

    monkeypatch.setattr(bridge, "confirm_article_operational_status", fail)

    result = execute_intake_placement(plan)

    assert result.ok is False
    assert result.status == PlacementExecutionStatus.REJECTED
    assert result.writer_called is False
    assert result.error_code == error_code


def test_payload_requires_exact_top_level_keys(monkeypatch):
    plan = _human_plan()
    payload = dict(plan.payload_preview)
    payload["unexpected"] = "value"
    plan = replace(plan, payload_preview=payload)

    monkeypatch.setattr(
        bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("writer called"),
    )

    result = execute_intake_placement(plan)

    assert result.error_code == ERROR_INVALID_PAYLOAD
    assert result.writer_called is False


def test_writer_arguments_reject_unknown_fields(monkeypatch):
    plan = _human_plan()
    payload = dict(plan.payload_preview)
    writer_arguments = dict(payload["writer_arguments"])
    writer_arguments["dispatch_target"] = "other_writer"
    payload["writer_arguments"] = writer_arguments
    plan = replace(plan, payload_preview=payload)

    monkeypatch.setattr(
        bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("writer called"),
    )

    result = execute_intake_placement(plan)

    assert result.error_code == ERROR_INVALID_WRITER_ARGUMENTS
    assert result.writer_called is False


def test_writer_arguments_require_all_mandatory_fields(monkeypatch):
    plan = _human_plan()
    payload = dict(plan.payload_preview)
    writer_arguments = dict(payload["writer_arguments"])
    writer_arguments.pop("audit_note")
    payload["writer_arguments"] = writer_arguments
    plan = replace(plan, payload_preview=payload)

    monkeypatch.setattr(
        bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("writer called"),
    )

    result = execute_intake_placement(plan)

    assert result.error_code == ERROR_INVALID_WRITER_ARGUMENTS
    assert result.writer_called is False


def test_source_evidence_must_match_plan_source_id(monkeypatch):
    plan = _human_plan()
    payload = dict(plan.payload_preview)
    source_evidence = dict(payload["source_evidence"])
    source_evidence["source_id"] = "human:OTHER"
    payload["source_evidence"] = source_evidence
    plan = replace(plan, payload_preview=payload)

    monkeypatch.setattr(
        bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("writer called"),
    )

    result = execute_intake_placement(plan)

    assert result.error_code == ERROR_INVALID_SOURCE_EVIDENCE
    assert result.writer_called is False


def test_bridge_has_one_static_writer_call_and_no_dynamic_dispatch():
    source = inspect.getsource(bridge)

    assert source.count("confirm_article_operational_status(") == 1
    assert "getattr(" not in source
    assert "globals(" not in source
    assert "import_module" not in source
    assert "retry" not in source.lower()
    assert "plan_intake_placements" not in source
    assert "for request in" not in source


def test_bridge_does_not_hardcode_article_12514():
    assert "12514" not in inspect.getsource(bridge)


@pytest.mark.parametrize(
    ("payload_preview", "error_code"),
    [
        (None, ERROR_INVALID_PAYLOAD),
        (
            {
                "writer_arguments": "not-a-mapping",
                "source_evidence": {"source_id": "human:SYNTH01"},
            },
            ERROR_INVALID_WRITER_ARGUMENTS,
        ),
        (
            {
                "writer_arguments": dict(
                    _human_plan().payload_preview["writer_arguments"]
                ),
                "source_evidence": "not-a-mapping",
            },
            ERROR_INVALID_SOURCE_EVIDENCE,
        ),
    ],
)
def test_invalid_payload_shapes_do_not_call_writer(
    monkeypatch,
    payload_preview,
    error_code,
):
    plan = replace(_human_plan(), payload_preview=payload_preview)

    monkeypatch.setattr(
        bridge,
        "confirm_article_operational_status",
        lambda **_kwargs: pytest.fail("writer called"),
    )

    result = execute_intake_placement(plan)

    assert result.ok is False
    assert result.status == PlacementExecutionStatus.REJECTED
    assert result.writer_called is False
    assert result.error_code == error_code
