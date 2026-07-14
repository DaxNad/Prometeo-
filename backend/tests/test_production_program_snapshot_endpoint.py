from __future__ import annotations

import inspect
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.production_program_snapshot import router
from app.services.production_program_snapshot_preview import RECORD_DELIMITER


VALID_INPUT = f"""\
PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50
DATA RICHIESTA CLIENTE: 2026-07-20
{RECORD_DELIMITER}
ORDINE: SYNTH-002
CODICE: ART-200
QTA: 25
CONSEGNA 22/07/2026
NOTA SINTETICA NON CLASSIFICATA
"""


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_valid_preview_preserves_contract_and_is_deterministic():
    payload = {"structured_text": VALID_INPUT, "source_id": "synthetic:test"}
    first = _client().post("/production-program-snapshot/preview", json=payload)
    second = _client().post("/production-program-snapshot/preview", json=payload)

    assert first.status_code == 200
    assert first.json() == second.json()
    data = first.json()
    assert data["source_id"] == "synthetic:test"
    assert data["source_type"] == "structured_text"
    assert data["period"] == "2026-W30"
    assert data["confidence"] == "LOW"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert len(data["orders"]) == 2
    assert data["orders"][0]["article_code"] == "ART-100"
    assert data["orders"][0]["quantity"] == 50
    assert data["orders"][0]["customer_requested_date"] == "2026-07-20"
    assert data["orders"][1]["article_code"] == "ART-200"
    assert data["orders"][1]["quantity"] == 25
    assert data["orders"][1]["customer_requested_date"] is None
    assert data["orders"][1]["ambiguous_fields"][0]["observed_label"] == "CONSEGNA"
    assert "NOTA SINTETICA NON CLASSIFICATA" in data["orders"][1]["unmatched_content"]
    assert data["orders"][0]["field_provenance"]["article_code"]["source_line"] == "CODICE: ART-100"
    assert data["requires_confirmation"] is True
    assert data["persisted"] is False
    assert data["writer_called"] is False
    assert data["planner_called"] is False
    assert data["pattern_learning_called"] is False


def test_empty_and_non_separable_inputs_fail_closed():
    responses = (
        (_client().post("/production-program-snapshot/preview", json={"structured_text": ""}), "empty_input"),
        (
            _client().post(
                "/production-program-snapshot/preview",
                json={"structured_text": "ORDINE: SYNTH-001\nCODICE: ART-100\nQTA: 50"},
            ),
            "record_delimiter_required",
        ),
    )
    for response, discrepancy in responses:
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["semantic_status"] == "BLOCCATO"
        assert data["discrepancies"] == [discrepancy]
        assert data["requires_confirmation"] is True
        assert data["persisted"] is False
        assert data["writer_called"] is False
        assert data["planner_called"] is False
        assert data["pattern_learning_called"] is False


def test_missing_field_is_declared_and_extra_field_is_rejected():
    missing = _client().post(
        "/production-program-snapshot/preview",
        json={
            "structured_text": f"PERIODO: 2026-W30\nORDINE: SYNTH-001\nCODICE: ART-100\nQTA: 50\n{RECORD_DELIMITER}\nORDINE: SYNTH-002\nQTA: 25"
        },
    )
    rejected = _client().post(
        "/production-program-snapshot/preview",
        json={"structured_text": VALID_INPUT, "persist_audit": True},
    )

    assert missing.status_code == 200
    assert {"record_index": 2, "field": "article_code"} in missing.json()["missing_fields"]
    assert rejected.status_code == 422


def test_route_is_registered_in_canonical_application():
    main_source = (Path(__file__).parents[1] / "app" / "main.py").read_text(
        encoding="utf-8"
    )

    assert (
        "from .api.production_program_snapshot import "
        "router as production_program_snapshot_router"
    ) in main_source
    assert (
        main_source.count("app.include_router(production_program_snapshot_router)")
        == 1
    )


def test_router_source_has_no_forbidden_integrations():
    from app.api import production_program_snapshot as endpoint

    source = inspect.getsource(endpoint)
    assert "ConfigDict(extra=\"forbid\")" in source
    assert "build_production_program_snapshot_preview" in source
    forbidden = (
        "Depends", "SMFAdapter", "create_engine", "DATABASE_URL", "persist",
        "audit", "write_", "open(", "Path(", "UploadFile", "pandas",
        "read_excel", "tesseract", "requests.", "httpx.", "planner",
        "agent_runtime", "pattern_learning", "tl_chat", "openai", "anthropic",
    )
    assert all(token not in source for token in forbidden)
