from __future__ import annotations

import base64

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.production_program_image_ocr_acquisition import (
    get_production_program_ocr_adapter,
    router,
)
from app.ingest.production_program_image_ocr_acquisition import OCRTextExtractionResult
from app.main import app as main_app


PNG = b"\x89PNG\r\n\x1a\nsynthetic-png"
JPEG = b"\xff\xd8\xffsynthetic-jpeg"
OCR_TEXT = """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data richiesta cliente: 2026-07-20
"""


class OCRAdapter:
    def __init__(self, *, text: str = OCR_TEXT, error_code: str | None = None) -> None:
        self.text = text
        self.error_code = error_code

    def extract_text(self, image_bytes, *, media_type, source_id):
        if self.error_code:
            return OCRTextExtractionResult(
                ok=False,
                provider="tesseract-local",
                error_code=self.error_code,
            )
        return OCRTextExtractionResult(
            ok=True,
            provider="synthetic-local",
            text=self.text,
        )


def client(adapter=None) -> TestClient:
    api = FastAPI()
    if adapter is not None:
        api.dependency_overrides[get_production_program_ocr_adapter] = lambda: adapter
    api.include_router(router)
    return TestClient(api)


def payload(image: bytes) -> dict[str, str]:
    return {"image_base64": base64.b64encode(image).decode("ascii")}


def assert_governance(data: dict[str, object]) -> None:
    assert data["requires_confirmation"] is True
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["persisted"] is False
    assert data["writer_called"] is False
    assert data["planner_called"] is False
    assert data["pattern_learning_called"] is False


def test_ready_preview_preserves_evidence_and_provenance() -> None:
    response = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire", json=payload(PNG)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "PREVIEW_READY"
    assert data["source_id"].startswith("production-program-image:sha256:")
    assert len(data["source_hash"]) == 64
    assert data["media_type"] == "image/png"
    assert data["provider"] == "synthetic-local"
    assert data["observed_text"] == OCR_TEXT
    assert data["normalized_lines"][0] == "PERIODO: 2026-W29"
    assert data["snapshot_preview"] is not None
    assert_governance(data)


def test_jpeg_media_type_is_preserved() -> None:
    data = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire", json=payload(JPEG)
    ).json()
    assert data["status"] == "PREVIEW_READY"
    assert data["media_type"] == "image/jpeg"
    assert_governance(data)


def test_missing_adapter_and_unsupported_bytes_fail_closed() -> None:
    missing = client().post(
        "/production-program/image-ocr/acquire", json=payload(PNG)
    ).json()
    unsupported = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire", json=payload(b"not-image")
    ).json()
    assert missing["status"] == "REJECTED"
    assert missing["error_code"] == "OCR_ADAPTER_REQUIRED"
    assert unsupported["status"] == "REJECTED"
    assert unsupported["error_code"] == "UNSUPPORTED_IMAGE_FORMAT"
    assert_governance(missing)
    assert_governance(unsupported)


def test_tesseract_timeout_and_failure_codes_are_preserved() -> None:
    for error_code in (
        "PRODUCTION_PROGRAM_TESSERACT_OCR_TIMEOUT",
        "PRODUCTION_PROGRAM_TESSERACT_OCR_FAILED",
    ):
        data = client(OCRAdapter(error_code=error_code)).post(
            "/production-program/image-ocr/acquire", json=payload(PNG)
        ).json()
        assert data["status"] == "OCR_FAILED"
        assert data["error_code"] == error_code
        assert data["provider"] == "tesseract-local"
        assert_governance(data)


def test_blocked_preview_preserves_raw_text() -> None:
    raw = "unmatched production program evidence"
    data = client(OCRAdapter(text=raw)).post(
        "/production-program/image-ocr/acquire", json=payload(PNG)
    ).json()
    assert data["status"] == "PREVIEW_BLOCKED"
    assert data["observed_text"] == raw
    assert data["normalized_lines"] == [raw]
    assert_governance(data)


def test_invalid_base64_and_invalid_schema_return_422() -> None:
    invalid = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire",
        json={"image_base64": "not-valid%%%"},
    )
    missing = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire", json={}
    )
    empty = client(OCRAdapter()).post(
        "/production-program/image-ocr/acquire", json={"image_base64": ""}
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"] == "INVALID_IMAGE_BASE64"
    assert missing.status_code == 422
    assert empty.status_code == 422


def test_router_is_registered_in_main_app() -> None:
    main_app.dependency_overrides[get_production_program_ocr_adapter] = lambda: OCRAdapter()
    try:
        response = TestClient(main_app).post(
            "/production-program/image-ocr/acquire", json=payload(PNG)
        )
    finally:
        main_app.dependency_overrides.pop(get_production_program_ocr_adapter, None)
    assert response.status_code == 200
    assert response.json()["status"] == "PREVIEW_READY"
