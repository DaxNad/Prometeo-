from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app


client = TestClient(app)


@dataclass(frozen=True)
class _StubReadback:
    found: bool = True
    rendered_text: str = (
        "Evidenza TL persistita: presente\n"
        "confirmation_status: TL_CONFIRMED_PREVIEW\n"
        "confidence=DA_VERIFICARE\n"
        "requires_confirmation=true\n"
        "requires_persistence_review=true\n"
        "planner_eligible=false\n"
        "promoted_to_certo=false"
    )


def test_12514_confirmation_rendering_uses_readback_service_binding(
    monkeypatch,
    tmp_path,
):
    preview_root = tmp_path / "spec_intake_preview"
    preview_root.mkdir(parents=True)

    (preview_root / "12514_metadata_preview.json").write_text(
        """{
            "status": "PREVIEW_ONLY",
            "confidence": "DA_VERIFICARE",
            "planner_eligible": false,
            "requires_tl_confirmation": true,
            "article": {
                "articolo": "12514",
                "codice": "7056055000A0",
                "disegno": "A1675003603",
                "rev": "6"
            }
        }""",
        encoding="utf-8",
    )

    calls = []

    def fake_readback_service(*, article, confirmation_root):
        calls.append((article, confirmation_root))
        return _StubReadback()

    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", preview_root)
    monkeypatch.setattr(
        tl_chat_api,
        "CONFIRMATION_12514_PATH",
        tmp_path / "spec_intake_confirmation" / "12514_confirmation.json",
    )
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", tmp_path / "specs_finitura")
    monkeypatch.setattr(tl_chat_api, "_response_from_article_summary", lambda _article: None)
    monkeypatch.setattr(
        tl_chat_api,
        "build_confirmation_evidence_readback",
        fake_readback_service,
    )

    response = client.post(
        "/tl/chat",
        json={
            "question": "Render conferma TL per articolo 12514",
            "context": {"article": "12514"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert calls == [
        (
            "12514",
            tmp_path / "spec_intake_confirmation",
        )
    ]

    assert data["ok"] is True
    assert data["confidence"] == "DA_VERIFICARE"
    assert data["requires_confirmation"] is True
    assert "Evidenza TL persistita: presente" in data["answer"]
    assert "planner_eligible=false" in data["answer"]
    assert "promoted_to_certo=false" in data["answer"]
    assert "non autorizza pianificazione" in data["risk"]
