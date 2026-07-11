from __future__ import annotations

import base64

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.article_specification_acquisition import (
    get_article_specification_ocr_adapter,
    router,
)
from app.ingest.article_specification_image_acquisition import (
    OCRTextExtractionResult,
)
from app.main import app as main_app


SYNTHETIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAF"
    "gAI/ScL9WQAAAABJRU5ErkJggg=="
)


class FakeOCRAdapter:
    def extract_text(self, image_bytes, *, media_type, source_id):
        return OCRTextExtractionResult(
            ok=True,
            text="""\
ARTICOLO: SYNTH-API-01
OPERAZIONI
LAVAGGIO
ASSEMBLAGGIO
COMPONENTI
468922 GUAINA
""",
        )


def _client(*, ocr_adapter=None) -> TestClient:
    api = FastAPI()
    if ocr_adapter is not None:
        api.dependency_overrides[get_article_specification_ocr_adapter] = (
            lambda: ocr_adapter
        )
    api.include_router(router)
    return TestClient(api)


def _payload() -> dict[str, str]:
    return {
        "image_base64": base64.b64encode(SYNTHETIC_PNG).decode("ascii"),
    }


def test_article_specification_acquisition_endpoint_exposes_review_only_binding():
    response = _client(ocr_adapter=FakeOCRAdapter()).post(
        "/article-specification/acquire",
        json=_payload(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["status"] == "BOUND"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["writer_called"] is False
    assert data["persisted"] is False
    assert data["requires_review"] is True

    assert data["acquisition"]["ok"] is True
    assert data["acquisition"]["status"] == "EXTRACTED"
    assert data["acquisition"]["media_type"] == "image/png"
    assert data["acquisition"]["error_code"] is None

    assert data["review_payloads"]
    assert all(
        item["semantic_status"] == "DA_VERIFICARE"
        for item in data["review_payloads"]
    )
    assert data["facade_results"]
    assert all(item["writer_called"] is False for item in data["facade_results"])
    assert all(item["status"] == "NOT_EXECUTED" for item in data["facade_results"])


def test_article_specification_acquisition_endpoint_fails_closed_without_ocr_adapter():
    response = _client().post(
        "/article-specification/acquire",
        json=_payload(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert data["status"] == "REJECTED"
    assert data["acquisition"]["status"] == "REJECTED"
    assert data["acquisition"]["error_code"] == "OCR_ADAPTER_REQUIRED"
    assert data["error_code"] == "ACQUISITION_NOT_EXTRACTED"
    assert data["writer_called"] is False
    assert data["persisted"] is False
    assert data["requires_review"] is True
    assert data["review_payloads"] == []
    assert data["facade_results"] == []


def test_article_specification_acquisition_endpoint_rejects_invalid_base64():
    response = _client(ocr_adapter=FakeOCRAdapter()).post(
        "/article-specification/acquire",
        json={"image_base64": "not-valid-base64%%%"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "INVALID_IMAGE_BASE64"


def test_article_specification_acquisition_router_is_registered_in_main_app():
    main_app.dependency_overrides[get_article_specification_ocr_adapter] = (
        lambda: FakeOCRAdapter()
    )
    try:
        response = TestClient(main_app).post(
            "/article-specification/acquire",
            json=_payload(),
        )
    finally:
        main_app.dependency_overrides.pop(
            get_article_specification_ocr_adapter,
            None,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "BOUND"
