from __future__ import annotations

import base64
import hashlib
import inspect

import pytest

from app.ingest import article_specification_image_acquisition as acquisition
from app.ingest.ocr_parser import parse_ocr_order_rows


SYNTHETIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAF"
    "gAI/ScL9WQAAAABJRU5ErkJggg=="
)

OCR_TEXT = """\
ARTICOLO: 99878
OPERAZIONI
LAVAGGIO
COLLAUDO A PRESSIONE
"""


class FakeOCRAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def extract_text(self, image_bytes, *, media_type, source_id):
        self.calls.append((image_bytes, media_type, source_id))
        return self.result


def test_valid_image_fake_ocr_calls_governed_parser_and_keeps_route_unconfirmed(
    monkeypatch,
):
    parser_calls = []
    governed_parser = acquisition.parse_article_specification_rows

    def parse_spy(rows, *, source_id):
        parser_calls.append((tuple(rows), source_id))
        return governed_parser(rows, source_id=source_id)

    monkeypatch.setattr(acquisition, "parse_article_specification_rows", parse_spy)
    ocr = FakeOCRAdapter(
        acquisition.OCRTextExtractionResult(ok=True, text=OCR_TEXT)
    )

    result = acquisition.acquire_article_specification_image(
        image_bytes=SYNTHETIC_PNG,
        ocr_adapter=ocr,
    )

    assert result.ok is True
    assert result.status == acquisition.ImageAcquisitionStatus.EXTRACTED
    assert result.media_type == "image/png"
    assert result.extracted_text == OCR_TEXT
    assert result.normalized_lines == (
        "ARTICOLO: 99878",
        "OPERAZIONI",
        "LAVAGGIO",
        "COLLAUDO A PRESSIONE",
    )
    assert len(ocr.calls) == 1
    assert len(parser_calls) == 1
    assert parser_calls[0] == (result.normalized_lines, result.source_id)
    assert result.parser_result is not None
    assert result.parser_result.ok is True

    assert all(
        payload["semantic_status"] == "DA_VERIFICARE"
        for payload in result.parser_result.payloads
    )
    route_payloads = [
        payload
        for payload in result.parser_result.payloads
        if payload["field_name"] == "operation"
    ]
    assert route_payloads
    assert all(
        payload["context"]["route_status"] == "DA_VERIFICARE"
        for payload in route_payloads
    )


def test_hash_and_source_id_are_deterministic_for_path_and_bytes(tmp_path):
    image_path = tmp_path / "synthetic-spec.png"
    image_path.write_bytes(SYNTHETIC_PNG)
    expected_hash = hashlib.sha256(SYNTHETIC_PNG).hexdigest()
    ocr = FakeOCRAdapter(
        acquisition.OCRTextExtractionResult(ok=True, text=OCR_TEXT)
    )

    from_bytes = acquisition.acquire_article_specification_image(
        image_bytes=SYNTHETIC_PNG,
        ocr_adapter=ocr,
    )
    from_path = acquisition.acquire_article_specification_image(
        image_path=image_path,
        ocr_adapter=ocr,
    )

    assert from_bytes.source_hash == expected_hash
    assert from_path.source_hash == expected_hash
    assert from_bytes.source_id == f"article-spec-image:sha256:{expected_hash}"
    assert from_path.source_id == from_bytes.source_id
    assert image_path.read_bytes() == SYNTHETIC_PNG


@pytest.mark.parametrize(
    ("kwargs", "error_code"),
    [
        ({}, acquisition.ERROR_IMAGE_INPUT_REQUIRED),
        ({"image_bytes": b""}, acquisition.ERROR_EMPTY_IMAGE),
        ({"image_bytes": b"not-an-image"}, acquisition.ERROR_UNSUPPORTED_IMAGE_FORMAT),
    ],
)
def test_missing_or_invalid_image_is_rejected_without_ocr(kwargs, error_code):
    ocr = FakeOCRAdapter(
        acquisition.OCRTextExtractionResult(ok=True, text=OCR_TEXT)
    )

    result = acquisition.acquire_article_specification_image(
        ocr_adapter=ocr,
        **kwargs,
    )

    assert result.ok is False
    assert result.status == acquisition.ImageAcquisitionStatus.REJECTED
    assert result.error_code == error_code
    assert ocr.calls == []
    assert result.parser_result is None


def test_ocr_error_is_propagated_without_parser_or_persistence(monkeypatch, tmp_path):
    monkeypatch.setattr(
        acquisition,
        "parse_article_specification_rows",
        lambda *_args, **_kwargs: pytest.fail("governed parser called"),
    )
    ocr = FakeOCRAdapter(
        acquisition.OCRTextExtractionResult(
            ok=False,
            error_code=acquisition.ERROR_OCR_EXTRACTION_FAILED,
        )
    )

    result = acquisition.acquire_article_specification_image(
        image_bytes=SYNTHETIC_PNG,
        ocr_adapter=ocr,
    )

    assert result.ok is False
    assert result.status == acquisition.ImageAcquisitionStatus.OCR_FAILED
    assert result.error_code == acquisition.ERROR_OCR_EXTRACTION_FAILED
    assert result.extracted_text == ""
    assert result.normalized_lines == ()
    assert result.parser_result is None
    assert list(tmp_path.iterdir()) == []


def test_acquisition_is_read_only_and_does_not_bind_order_ocr_or_runtime():
    source = inspect.getsource(acquisition)

    required = (
        "parse_article_specification_rows",
        "Protocol",
        "sha256",
    )
    forbidden = (
        "parse_ocr_order_rows",
        "structured_intake",
        "confirm_article_operational_status",
        "execution_bridge",
        "planner",
        "write_text",
        "write_bytes",
        "requests.",
        "httpx.",
        "openai",
        "anthropic",
        "tesseract",
        "pytesseract",
        "opencv",
        "cv2",
    )
    assert all(token in source for token in required)
    assert all(token not in source for token in forbidden)


def test_order_ocr_parser_contract_is_unchanged():
    result = parse_ocr_order_rows(
        """
        ID ordine: SYNTH-ORDER-001
        Codice: SYNTH-CODE
        QTA: 2
        """
    )

    assert result["parsed_order"]["order_id"] == "SYNTH-ORDER-001"
    assert result["parsed_order"]["codice"] == "SYNTH-CODE"
    assert result["parsed_order"]["qta"] == "2"
