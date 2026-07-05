import json

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app
from app.services.tl_chat_confirmation_rendering import (
    TLChatConfirmationRenderingInput,
    build_confirmation_rendering,
)


client = TestClient(app)

ARTICLE = "12066"


def _write_preview(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{ARTICLE}_metadata_preview.json").write_text(
        json.dumps(
            {
                "capability": f"SPEC_INTAKE_{ARTICLE}_PREVIEW_001",
                "status": "PREVIEW_ONLY",
                "confidence": "DA_VERIFICARE",
                "planner_eligible": False,
                "requires_tl_confirmation": True,
                "article": {
                    "articolo": ARTICLE,
                    "codice": "TEST-CODE",
                    "disegno": "TEST-DRAWING",
                    "rev": "1",
                },
            }
        ),
        encoding="utf-8",
    )


def test_confirmation_rendering_accepts_safe_non_12514_article():
    result = build_confirmation_rendering(
        TLChatConfirmationRenderingInput(
            article=ARTICLE,
            question_id="Q1",
            tl_answer_state="UNKNOWN",
            resulting_status="DA_VERIFICARE",
            candidate_data={"codice": "TEST-CODE"},
            missing_data=["conferma TL"],
            next_safe_action="mantenere DA_VERIFICARE",
        )
    )

    assert result.article == ARTICLE
    assert result.confidence == "DA_VERIFICARE"
    assert result.forbidden_runtime_effects["planner_enablement"] is False
    assert f"Articolo: {ARTICLE}" in result.rendered_text


def test_generic_confirmation_route_persists_governed_evidence(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    confirmation_root = tmp_path / "spec_intake_confirmation"
    _write_preview(preview_root)

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_CONFIRMATION_ROOT",
        confirmation_root,
        raising=False,
    )

    response = client.post(
        f"/tl/{ARTICLE}/confirmation",
        json={
            "article": ARTICLE,
            "confirmation_action": "confirm_preview",
            "confirmed_by": "TL",
            "confirmed_fields": ["codice", "disegno", "rev"],
            "notes": "Conferma TL di test",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["article"] == ARTICLE
    assert body["confidence"] == "DA_VERIFICARE"
    assert body["planner_eligible"] is False
    assert body["promoted_to_certo"] is False

    record = json.loads(
        (confirmation_root / f"{ARTICLE}_confirmation.json").read_text(
            encoding="utf-8"
        )
    )
    assert record["schema"] == "TL_CHAT_CONFIRMATION_RECORD_V1"
    assert record["article"] == ARTICLE
    assert record["requires_persistence_review"] is True
    assert record["planner_eligible"] is False
    assert record["promoted_to_certo"] is False


def test_generic_confirmation_route_rejects_article_without_preview(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_PREVIEW_ROOT",
        tmp_path / "missing_preview",
    )
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_CONFIRMATION_ROOT",
        tmp_path / "confirmations",
        raising=False,
    )

    response = client.post(
        f"/tl/{ARTICLE}/confirmation",
        json={
            "article": ARTICLE,
            "confirmation_action": "confirm_preview",
            "confirmed_by": "TL",
            "confirmed_fields": ["codice"],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "preview_source_missing"


def test_generic_confirmation_route_rejects_article_mismatch(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    _write_preview(preview_root)

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_CONFIRMATION_ROOT",
        tmp_path / "confirmations",
    )

    response = client.post(
        f"/tl/{ARTICLE}/confirmation",
        json={
            "article": "12191A",
            "confirmation_action": "confirm_preview",
            "confirmed_by": "TL",
            "confirmed_fields": ["codice"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "article_mismatch"


def test_generic_confirmation_route_blocks_overwrite(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    confirmation_root = tmp_path / "spec_intake_confirmation"
    _write_preview(preview_root)
    confirmation_root.mkdir(parents=True)

    existing = confirmation_root / f"{ARTICLE}_confirmation.json"
    existing.write_text('{"existing": true}\n', encoding="utf-8")

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_CONFIRMATION_ROOT",
        confirmation_root,
    )

    response = client.post(
        f"/tl/{ARTICLE}/confirmation",
        json={
            "article": ARTICLE,
            "confirmation_action": "confirm_preview",
            "confirmed_by": "TL",
            "confirmed_fields": ["codice"],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "confirmation_record_already_exists"
    assert existing.read_text(encoding="utf-8") == '{"existing": true}\n'


def test_generic_confirmation_persistence_rejects_unsafe_article(
    monkeypatch,
    tmp_path,
):
    confirmation_root = tmp_path / "spec_intake_confirmation"
    monkeypatch.setattr(
        tl_chat_api,
        "SPEC_INTAKE_CONFIRMATION_ROOT",
        confirmation_root,
    )

    try:
        tl_chat_api._persist_article_confirmation(
            article="../12514",
            confirmed_fields=["codice"],
            notes="",
        )
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400
        assert getattr(exc, "detail", None) == "invalid_article_code"
    else:
        raise AssertionError("Expected unsafe article rejection")

    assert not confirmation_root.exists()
