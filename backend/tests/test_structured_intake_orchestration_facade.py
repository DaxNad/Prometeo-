import inspect

import pytest

from app.services import structured_intake_orchestration_facade as facade
from app.services.intake_destination_classifier import IntakeItem
from app.services.intake_single_item_orchestrator import (
    IntakeOrchestrationStatus,
    IntakeSingleItemOrchestrationResult,
)
from app.services.structured_intake_item_adapter import (
    ERROR_INVALID_PAYLOAD,
    StructuredIntakeAdapterStatus,
)
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeStatus,
    process_structured_intake_payload,
)


def _payload(**overrides):
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
    return payload


def test_valid_payload_builds_item_and_calls_orchestrator_once(monkeypatch):
    calls = []

    def orchestrate(item, *, requested_by_role=None):
        calls.append((item, requested_by_role))
        return IntakeSingleItemOrchestrationResult(
            ok=True,
            status=IntakeOrchestrationStatus.EXECUTED,
            classification=object(),
            plan=object(),
            execution=object(),
            writer_called=True,
            source_id=item.source_id,
        )

    monkeypatch.setattr(facade, "orchestrate_intake_item", orchestrate)

    result = process_structured_intake_payload(
        _payload(),
        requested_by_role="RESPONSABILE_PRODUZIONE",
    )

    assert len(calls) == 1
    assert isinstance(calls[0][0], IntakeItem)
    assert calls[0][1] == "RESPONSABILE_PRODUZIONE"
    assert result.ok is True
    assert result.status == StructuredIntakeFacadeStatus.ORCHESTRATED
    assert result.adapter_result.status == StructuredIntakeAdapterStatus.BUILT
    assert result.orchestration_result is not None
    assert result.writer_called is True


@pytest.mark.parametrize("payload", [None, [], "invalid", {"field_name": "", "source_id": ""}])
def test_rejected_adapter_result_does_not_call_orchestrator(monkeypatch, payload):
    monkeypatch.setattr(
        facade,
        "orchestrate_intake_item",
        lambda *_args, **_kwargs: pytest.fail("orchestrator called"),
    )

    result = process_structured_intake_payload(payload)

    assert result.ok is False
    assert result.status == StructuredIntakeFacadeStatus.REJECTED
    assert result.adapter_result.ok is False
    assert result.orchestration_result is None
    assert result.writer_called is False


def test_invalid_payload_preserves_adapter_error(monkeypatch):
    monkeypatch.setattr(
        facade,
        "orchestrate_intake_item",
        lambda *_args, **_kwargs: pytest.fail("orchestrator called"),
    )

    result = process_structured_intake_payload(None)

    assert result.error_code == ERROR_INVALID_PAYLOAD


def test_orchestration_failure_is_preserved(monkeypatch):
    monkeypatch.setattr(
        facade,
        "orchestrate_intake_item",
        lambda item, *, requested_by_role=None: IntakeSingleItemOrchestrationResult(
            ok=False,
            status=IntakeOrchestrationStatus.NOT_EXECUTED,
            classification=object(),
            plan=object(),
            execution=None,
            writer_called=False,
            source_id=item.source_id,
            error_code="CLASSIFICATION_NOT_READY",
        ),
    )

    result = process_structured_intake_payload(_payload())

    assert result.ok is False
    assert result.status == StructuredIntakeFacadeStatus.NOT_EXECUTED
    assert result.orchestration_result is not None
    assert result.writer_called is False
    assert result.error_code == "CLASSIFICATION_NOT_READY"


def test_execution_failure_is_not_reported_as_not_executed(monkeypatch):
    monkeypatch.setattr(
        facade,
        "orchestrate_intake_item",
        lambda item, *, requested_by_role=None: IntakeSingleItemOrchestrationResult(
            ok=False,
            status=IntakeOrchestrationStatus.EXECUTION_FAILED,
            classification=object(),
            plan=object(),
            execution=object(),
            writer_called=True,
            source_id=item.source_id,
            error_code="WRITER_FAILED",
        ),
    )

    result = process_structured_intake_payload(_payload())

    assert result.status == StructuredIntakeFacadeStatus.ORCHESTRATION_FAILED
    assert result.writer_called is True
    assert result.error_code == "WRITER_FAILED"


def test_facade_has_no_batch_dynamic_dispatch_retry_or_io():
    source = inspect.getsource(facade)

    forbidden = (
        "build_intake_items",
        "classify_intake_items",
        "plan_intake_placements",
        "for payload in",
        "getattr(",
        "globals(",
        "import_module",
        "retry",
        "open(",
        "read_text",
        "write_text",
        "requests.",
        "httpx.",
    )
    assert all(token not in source for token in forbidden)
    assert source.count("build_intake_item(") == 1
    assert source.count("orchestrate_intake_item(") == 1


def test_facade_does_not_hardcode_article_12514():
    assert "12514" not in inspect.getsource(facade)
