from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


TECHNICAL_NOISE = (
    "traceback",
    "pytest",
    "sqlalchemy",
    "stacktrace",
    "uvicorn",
)


@pytest.fixture
def isolated_tl_sources(monkeypatch, tmp_path):
    registry = tmp_path / "article_lifecycle_registry.json"
    staging = tmp_path / "codici_staging_preview.json"
    intake = tmp_path / "TL_REAL_SPEC_INTAKE_001.json"
    preview = tmp_path / "article_route_matrix.preview.json"

    registry.write_text(json.dumps({}), encoding="utf-8")
    staging.write_text(json.dumps({"items": []}), encoding="utf-8")
    intake.write_text(json.dumps({"items": []}), encoding="utf-8")
    preview.write_text(json.dumps({"profiles": {}}), encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "LIFECYCLE_REGISTRY", registry)
    monkeypatch.setattr(tl_chat_api, "CODICI_STAGING_PREVIEW", staging)
    monkeypatch.setattr(tl_chat_api, "TL_REAL_SPEC_INTAKE", intake)
    monkeypatch.setattr(tl_chat_api, "ARTICLE_ROUTE_MATRIX_PREVIEW", preview)
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", lambda _article: {"ok": False})

    return {
        "registry": registry,
        "staging": staging,
        "intake": intake,
        "preview": preview,
    }


def _ask(question: str, context: dict[str, str] | None = None) -> dict:
    client = TestClient(app)
    payload: dict[str, object] = {"question": question}
    if context is not None:
        payload["context"] = context

    response = client.post("/tl/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "TL_CHAT_CONTRACT_V1"
    assert data["technical_details_hidden"] is True
    return data


def _combined(data: dict) -> str:
    return " ".join(str(data.get(key) or "") for key in ("answer", "risk", "recommended_action"))


def _assert_operational_shape(data: dict) -> None:
    combined = _combined(data)
    assert data["answer"]
    assert data.get("risk")
    assert data.get("recommended_action")
    assert not any(token in combined.lower() for token in TECHNICAL_NOISE)


def test_practical_q1_certain_article_12066(monkeypatch, isolated_tl_sources):
    def summary(article: str) -> dict:
        assert article == "12066"
        return {
            "ok": True,
            "article": "12066",
            "confidence": "CERTO",
            "route": ["HENN", "ZAW1", "PIDMILL", "CP"],
            "signals": {
                "has_henn": True,
                "has_zaw1": True,
                "has_zaw2": False,
                "primary_zaw_station": "ZAW1",
                "has_pidmill": True,
                "cp_required": True,
                "cp_machine_mode": "VERTICALE_DUE_PIANI",
                "shared_components": ["468728", "468796"],
            },
            "criticalities": [
                "Discrepanza confermata da TL: ZAW1 obbligatoria, ZAW2 non automatica."
            ],
            "tl_action": "Seguire route confermata e usare criticita come checklist TL.",
        }

    monkeypatch.setattr(tl_chat_api, "build_article_tl_summary", summary)

    data = _ask("12066?")
    _assert_operational_shape(data)

    assert data["confidence"] == "CERTO"
    assert data["requires_confirmation"] is False
    assert "12066" in data["answer"]
    assert "Route:" in data["answer"]
    assert "HENN" in data["answer"]
    assert "ZAW1" in data["answer"]
    assert "ZAW2" in data["answer"]
    assert "PIDMILL" in data["answer"]
    assert "CP finale obbligatorio" in data["answer"]
    assert "VERTICALE_DUE_PIANI" in data["answer"]
    assert "Vincoli:" in data["answer"]
    assert "Azione:" in data["answer"]


def test_practical_q2_inferred_article_12070_requires_confirmation(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps({"12070": {"status": "NEW_ENTRY", "source": "tl"}}),
        encoding="utf-8",
    )

    data = _ask("12070?")
    _assert_operational_shape(data)

    assert data["confidence"] != "CERTO"
    assert data["requires_confirmation"] is True
    assert "12070" in data["answer"]
    assert "NEW_ENTRY" in data["answer"]
    assert "confermat" in _combined(data).lower()


def test_practical_q3_lists_codes_to_verify(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12402": {"status": "DA_VERIFICARE", "source": "tl"},
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono da verificare?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12402" in data["answer"]
    assert "DA_VERIFICARE" in data["answer"]
    assert "12053" not in data["answer"]
    assert "12410" not in data["answer"]
    assert "Verifica TL richiesta" in data["recommended_action"]


def test_practical_q4_lists_densification_candidates_without_planner_promotion(isolated_tl_sources):
    isolated_tl_sources["staging"].write_text(
        json.dumps(
            {
                "items": [
                    {
                        "codice": "12056",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "REVIEW_BEFORE_STAGING",
                    },
                    {
                        "codice": "12410",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "REVIEW_HIGH_PRIORITY",
                    },
                    {
                        "codice": "12402",
                        "tl_decision": "PENDING",
                        "staging_status": "PREVIEW_ONLY",
                        "next_action": "TL_REVIEW_REQUIRED",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici posso densificare?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12056" in data["answer"]
    assert "12410" in data["answer"]
    assert "12402" not in data["answer"]
    assert "staging preview" in data["risk"]
    assert "conferma TL" in data["risk"]


def test_practical_q5_lists_fuori_produzione_as_consultive_only(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
                "12402": {
                    "status": "CUSTOMER_REQUEST_ONLY",
                    "source": "tl",
                    "note": "Fuori produzione standard, solo su richiesta cliente.",
                },
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono fuori produzione?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12053" in data["answer"]
    assert "12402" in data["answer"]
    assert "12410" not in data["answer"]
    assert "FUORI_PRODUZIONE" in data["answer"]
    assert "richiesta cliente" in _combined(data).lower()
    assert "non devono essere promossi automaticamente" in data["risk"]


def test_practical_q6_lists_new_entry_as_consultable_not_auto_plannable(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12410": {"status": "NEW_ENTRY", "source": "tl"},
                "12402": {"status": "DA_VERIFICARE", "source": "tl"},
                "12053": {"status": "FUORI_PRODUZIONE", "source": "tl"},
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Quali codici sono new entry?")
    _assert_operational_shape(data)

    assert data["requires_confirmation"] is True
    assert "12410" in data["answer"]
    assert "NEW_ENTRY" in data["answer"]
    assert "12402" not in data["answer"]
    assert "12053" not in data["answer"]
    assert "conferma TL" in data["risk"]


def test_practical_q7_12402_verification_respects_customer_request_only(isolated_tl_sources):
    isolated_tl_sources["registry"].write_text(
        json.dumps(
            {
                "12402": {
                    "status": "CUSTOMER_REQUEST_ONLY",
                    "source": "tl",
                    "note": "Fuori produzione standard, solo su richiesta cliente.",
                }
            }
        ),
        encoding="utf-8",
    )

    data = _ask("Il 12402 e da verificare?")
    _assert_operational_shape(data)

    assert data["confidence"] != "CERTO"
    assert data["requires_confirmation"] is True
    assert "12402" in data["answer"]
    assert "fuori produzione standard" in data["answer"]
    assert "richiesta cliente" in _combined(data).lower()
    assert "non pianificare automaticamente" in data["risk"]
