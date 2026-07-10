from app.api import tl_chat as tl_chat_api


def test_certain_article_without_route_does_not_claim_confirmed_route(monkeypatch):
    monkeypatch.setattr(
        tl_chat_api,
        "build_article_tl_summary",
        lambda article: {
            "ok": True,
            "article": article,
            "confidence": "CERTO",
            "planner_eligible": True,
            "route": [],
            "route_status": None,
            "signals": {},
            "criticalities": [],
            "tl_action": "Seguire lo stato operativo confermato.",
        },
    )

    response = tl_chat_api._response_from_article_summary("12514")

    assert response is not None
    assert response.confidence == "CERTO"
    assert "usa route confermata" not in response.answer
    assert "stato articolo confermato; route da verificare" in response.answer


def test_certain_article_with_route_can_claim_confirmed_route(monkeypatch):
    monkeypatch.setattr(
        tl_chat_api,
        "build_article_tl_summary",
        lambda article: {
            "ok": True,
            "article": article,
            "confidence": "CERTO",
            "planner_eligible": True,
            "route": ["ZAW1", "CP"],
            "route_status": "CONFIRMED",
            "signals": {},
            "criticalities": [],
            "tl_action": "Seguire la route confermata.",
        },
    )

    response = tl_chat_api._response_from_article_summary("12073")

    assert response is not None
    assert "usa route confermata" in response.answer
