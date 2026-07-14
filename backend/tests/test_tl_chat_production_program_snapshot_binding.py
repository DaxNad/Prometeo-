from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.services.production_program_snapshot_preview import (
    build_production_program_snapshot_preview,
)


MARKER = "PROMETEO_PROGRAM_SNAPSHOT_PREVIEW_V1"

VALID_BODY = """PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50
DATA RICHIESTA CLIENTE: 20/07/2026
--- RECORD ---
ORDINE: SYNTH-002
CODICE: ART-200
QTA: 25
CONSEGNA 22/07/2026"""


def _post(path: str, question: str):
    from app.main import app

    client = TestClient(app)
    return client.post(
        path,
        json={
            "question": question,
            "context": {},
        },
    )


def _raise_if_called(name: str):
    def guard(*args: Any, **kwargs: Any):
        raise AssertionError(f"{name} must not be called")

    return guard


def test_exact_marker_activates_snapshot_preview():
    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    assert response.status_code == 200
    data = response.json()
    preview = data["production_program_snapshot_preview"]

    assert data["requires_confirmation"] is True
    assert data["source"] == "production_program_snapshot_preview"
    assert preview["period"] == "2026-W30"
    assert len(preview["orders"]) == 2
    assert "ANTEPRIMA PROGRAMMA PRODUZIONE" in data["answer"]
    assert "Ordini rilevati: 2" in data["answer"]
    assert "Nessun dato è stato persistito." in data["answer"]


def test_valid_body_matches_existing_service_output():
    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    assert response.status_code == 200
    assert (
        response.json()["production_program_snapshot_preview"]
        == build_production_program_snapshot_preview(VALID_BODY)
    )


def test_marker_only_returns_blocked_preview():
    response = _post("/tl/chat", MARKER)

    assert response.status_code == 200
    data = response.json()
    preview = data["production_program_snapshot_preview"]

    assert preview["ok"] is False
    assert preview["semantic_status"] == "BLOCCATO"
    assert preview["discrepancies"] == ["empty_input"]
    assert data["requires_confirmation"] is True


def test_missing_delimiter_remains_fail_closed():
    body = """PERIODO: 2026-W30
ORDINE: SYNTH-001
CODICE: ART-100
QTA: 50"""

    response = _post("/tl/chat", f"{MARKER}\n{body}")

    assert response.status_code == 200
    preview = response.json()["production_program_snapshot_preview"]
    assert preview["ok"] is False
    assert preview["semantic_status"] == "BLOCCATO"
    assert preview["discrepancies"] == [
        "record_delimiter_required"
    ]


def test_generic_date_remains_ambiguous():
    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    preview = response.json()["production_program_snapshot_preview"]
    second = preview["orders"][1]

    assert second["customer_requested_date"] is None
    assert second["ambiguous_fields"]
    assert second["ambiguous_fields"][0]["raw_value"] == "22/07/2026"


def test_no_side_effect_flags_remain_false():
    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    preview = response.json()["production_program_snapshot_preview"]
    assert preview["requires_confirmation"] is True
    assert preview["persisted"] is False
    assert preview["writer_called"] is False
    assert preview["planner_called"] is False
    assert preview["pattern_learning_called"] is False
    assert preview["semantic_status"] != "CERTO"


def test_explicit_path_bypasses_all_ordinary_tl_chat_retrieval(
    monkeypatch,
):
    monkeypatch.setattr(
        tl_chat_api,
        "_build_contract_response",
        _raise_if_called("_build_contract_response"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "build_governed_retrieval_pack",
        _raise_if_called("build_governed_retrieval_pack"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_load_lifecycle_registry",
        _raise_if_called("_load_lifecycle_registry"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_load_local_specs_metadata",
        _raise_if_called("_load_local_specs_metadata"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_load_spec_intake_preview",
        _raise_if_called("_load_spec_intake_preview"),
    )
    monkeypatch.setattr(
        tl_chat_api,
        "_response_from_context_reader_bridge",
        _raise_if_called("_response_from_context_reader_bridge"),
    )

    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    assert response.status_code == 200
    assert (
        response.json()["production_program_snapshot_preview"]["ok"]
        is True
    )


def test_only_existing_snapshot_service_is_called(monkeypatch):
    calls: list[str] = []

    def snapshot_service(structured_text: str):
        calls.append(structured_text)
        return build_production_program_snapshot_preview(
            structured_text
        )

    monkeypatch.setattr(
        tl_chat_api,
        "build_production_program_snapshot_preview",
        snapshot_service,
    )

    response = _post("/tl/chat", f"{MARKER}\n{VALID_BODY}")

    assert response.status_code == 200
    assert calls == [VALID_BODY]


def test_near_miss_markers_do_not_activate():
    near_misses = [
        "Mostrami PROMETEO_PROGRAM_SNAPSHOT_PREVIEW_V1",
        "PROMETEO_PROGRAM_SNAPSHOT_PREVIEW",
        "prometeo_program_snapshot_preview_v1",
        "Vorrei importare il programma produzione",
        "Il programma contiene questi ordini...",
        f"Prima riga ordinaria\n{MARKER}\n{VALID_BODY}",
    ]

    for question in near_misses:
        response = _post("/tl/chat", question)
        assert response.status_code == 200
        assert (
            "production_program_snapshot_preview"
            not in response.json()
        )


def test_ordinary_tl_chat_behavior_is_unchanged():
    response = _post("/tl/chat", "Cosa devo verificare?")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["requires_confirmation"] is True
    assert "production_program_snapshot_preview" not in data


def test_public_and_legacy_routes_match():
    question = f"{MARKER}\n{VALID_BODY}"

    legacy = _post("/tl/chat", question)
    public = _post("/chat", question)

    assert legacy.status_code == 200
    assert public.status_code == 200
    assert public.json() == legacy.json()
