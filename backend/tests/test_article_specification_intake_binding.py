from __future__ import annotations

import base64
from dataclasses import replace
import inspect

import pytest

from app.ingest.article_specification_image_acquisition import (
    OCRTextExtractionResult,
    acquire_article_specification_image,
)
from app.services import article_specification_intake_binding as binding
from app.services.article_specification_intake_binding import (
    ArticleSpecificationIntakeBindingStatus,
    bind_article_specification_acquisition,
)
from app.services.structured_intake_orchestration_facade import (
    StructuredIntakeFacadeResult,
    StructuredIntakeFacadeStatus,
)


SYNTHETIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAF"
    "gAI/ScL9WQAAAABJRU5ErkJggg=="
)


class FakeOCRAdapter:
    def extract_text(self, image_bytes, *, media_type, source_id):
        return OCRTextExtractionResult(
            ok=True,
            text="""\
ARTICOLO: SYNTH-BIND-01
OPERAZIONI
LAVAGGIO
ASSEMBLAGGIO
COMPONENTI
468922 GUAINA
""",
        )


def _acquisition_result():
    return acquire_article_specification_image(
        image_bytes=SYNTHETIC_PNG,
        ocr_adapter=FakeOCRAdapter(),
    )


def test_binding_preserves_parser_order_and_calls_facade_once_per_payload(monkeypatch):
    acquisition = _acquisition_result()
    assert acquisition.parser_result is not None
    calls = []
    real_process = binding.process_structured_intake_payload

    def process_spy(payload, *, requested_by_role=None):
        calls.append((payload, requested_by_role))
        return real_process(payload, requested_by_role=requested_by_role)

    monkeypatch.setattr(binding, "process_structured_intake_payload", process_spy)

    result = bind_article_specification_acquisition(acquisition)

    assert result.status == ArticleSpecificationIntakeBindingStatus.BOUND
    assert len(calls) == len(acquisition.parser_result.payloads)
    assert [call[0] for call in calls] == list(acquisition.parser_result.payloads)
    assert [item.source_id for item in result.facade_results] == [
        acquisition.source_id
    ] * len(calls)


def test_da_verificare_acquisition_never_calls_writer_or_persists():
    acquisition = _acquisition_result()

    result = bind_article_specification_acquisition(acquisition)

    assert result.ok is True
    assert result.status == ArticleSpecificationIntakeBindingStatus.BOUND
    assert result.writer_called is False
    assert result.persisted is False
    assert result.requires_review is True
    assert result.semantic_status == "DA_VERIFICARE"
    assert result.facade_results
    assert all(item.writer_called is False for item in result.facade_results)
    assert all(
        item.status == StructuredIntakeFacadeStatus.NOT_EXECUTED
        for item in result.facade_results
    )


@pytest.mark.parametrize("invalid", [None, object(), "invalid"])
def test_invalid_acquisition_is_rejected_without_facade_call(monkeypatch, invalid):
    monkeypatch.setattr(
        binding,
        "process_structured_intake_payload",
        lambda *_args, **_kwargs: pytest.fail("facade called"),
    )

    result = bind_article_specification_acquisition(invalid)

    assert result.ok is False
    assert result.status == ArticleSpecificationIntakeBindingStatus.REJECTED
    assert result.facade_results == ()
    assert result.writer_called is False


def test_promoted_payload_is_rejected_before_facade_call(monkeypatch):
    acquisition = _acquisition_result()
    assert acquisition.parser_result is not None
    promoted = dict(acquisition.parser_result.payloads[0])
    promoted["semantic_status"] = "CERTO"
    parser_result = replace(acquisition.parser_result, payloads=(promoted,))
    acquisition = replace(acquisition, parser_result=parser_result)
    monkeypatch.setattr(
        binding,
        "process_structured_intake_payload",
        lambda *_args, **_kwargs: pytest.fail("facade called"),
    )

    result = bind_article_specification_acquisition(acquisition)

    assert result.ok is False
    assert result.error_code == binding.ERROR_UNSAFE_SEMANTIC_STATUS
    assert result.writer_called is False


def test_unexpected_writer_call_fails_closed(monkeypatch):
    acquisition = _acquisition_result()

    monkeypatch.setattr(
        binding,
        "process_structured_intake_payload",
        lambda payload, *, requested_by_role=None: StructuredIntakeFacadeResult(
            ok=True,
            status=StructuredIntakeFacadeStatus.ORCHESTRATED,
            adapter_result=object(),
            orchestration_result=object(),
            writer_called=True,
            source_id=payload["source_id"],
        ),
    )

    result = bind_article_specification_acquisition(acquisition)

    assert result.ok is False
    assert result.error_code == binding.ERROR_WRITER_BOUNDARY_VIOLATION
    assert result.writer_called is True
    assert result.persisted is False


def test_binding_has_no_io_ocr_parser_writer_or_article_hardcode():
    source = inspect.getsource(binding)

    required = (
        "ArticleSpecificationImageAcquisitionResult",
        "process_structured_intake_payload",
    )
    forbidden = (
        "acquire_article_specification_image",
        "parse_article_specification_rows",
        "confirm_article_operational_status",
        "execute_intake_placement",
        "open(",
        "read_text",
        "write_text",
        "12514",
    )
    assert all(token in source for token in required)
    assert all(token not in source for token in forbidden)
