from __future__ import annotations

import base64

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.production_program_image_ocr_acquisition import (
    get_production_program_ocr_adapter,
    router,
)
from app.ingest.production_program_image_ocr_acquisition import (
    OCRTextExtractionResult,
)


PNG_PAGE_1 = b"\x89PNG\r\n\x1a\nsynthetic-page-1"
PNG_PAGE_2 = b"\x89PNG\r\n\x1a\nsynthetic-page-2"

OCR_TEXT_BY_SOURCE_SUFFIX = {
    "synthetic-page-1": """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data richiesta cliente: 2026-07-20
""",
    "synthetic-page-2": """--- RECORD ---
ordine: ORD-002
codice: ART-002
qta: 8
scadenza: 2026-07-21
""",
}


class OCRAdapter:
    def extract_text(self, image_bytes, *, media_type, source_id):
        page_marker = image_bytes.decode("latin-1").splitlines()[-1]
        return OCRTextExtractionResult(
            ok=True,
            provider="synthetic-local",
            text=OCR_TEXT_BY_SOURCE_SUFFIX[page_marker],
        )


def client() -> TestClient:
    api = FastAPI()
    api.dependency_overrides[get_production_program_ocr_adapter] = OCRAdapter
    api.include_router(router)
    return TestClient(api)


def payload(*pages: bytes) -> dict[str, list[str]]:
    return {
        "images_base64": [
            base64.b64encode(page).decode("ascii")
            for page in pages
        ]
    }


def test_multipage_endpoint_returns_ordered_governed_preview() -> None:
    response = client().post(
        "/production-program/image-ocr/acquire-multipage",
        json=payload(PNG_PAGE_1, PNG_PAGE_2),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["status"] == "PREVIEW_READY"

    assert data["source_id"].startswith(
        "production-program-images:sha256:"
    )
    assert len(data["source_hash"]) == 64

    assert data["page_count"] == 2
    assert len(data["page_source_ids"]) == 2
    assert data["page_source_ids"][0].startswith(
        "production-program-image:sha256:"
    )
    assert data["page_source_ids"][1].startswith(
        "production-program-image:sha256:"
    )
    assert data["page_source_ids"][0] != data["page_source_ids"][1]

    assert data["provider"] == "synthetic-local"
    assert data["failed_page_number"] is None

    assert "ORD-001" in data["observed_text"]
    assert "ORD-002" in data["observed_text"]
    assert data["observed_text"].index("ORD-001") < data["observed_text"].index(
        "ORD-002"
    )

    assert data["snapshot_preview"] is not None

    assert data["requires_confirmation"] is True
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["persisted"] is False
    assert data["writer_called"] is False
    assert data["planner_called"] is False
    assert data["pattern_learning_called"] is False
