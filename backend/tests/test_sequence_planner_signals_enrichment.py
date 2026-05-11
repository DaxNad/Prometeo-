from app.services import sequence_planner as sp


def test_build_global_sequence_enriches_signals_from_article_profile(monkeypatch):
    monkeypatch.setattr(
        sp.sequence_planner_service,
        "BOARD_SOURCES",
        [{"view": "vw_fake_board", "station": "ZAW-1"}],
    )

    def fake_fetch_station_board(db_sess, view_name: str):
        return [
            {
                "priorita_operativa": 1,
                "articolo": "ART-WITH-PROFILE",
                "componenti_condivisi": "",
                "quantita": 3,
                "data_spedizione": None,
                "priorita_cliente": "MEDIA",
                "complessivo_articolo": "GRP-A",
                "postazione_critica": "ZAW-1",
                "azione_tl": "VERIFICA",
                "origine_logica": view_name,
            },
            {
                "priorita_operativa": 2,
                "articolo": "ART-NO-PROFILE",
                "componenti_condivisi": "",
                "quantita": 1,
                "data_spedizione": None,
                "priorita_cliente": "MEDIA",
                "complessivo_articolo": "GRP-B",
                "postazione_critica": "ZAW-2",
                "azione_tl": "MONITORA",
                "origine_logica": view_name,
            },
        ]

    def fake_resolve_article_profile(article_code: str):
        if article_code == "ART-WITH-PROFILE":
            return {
                "source": "TEST_PROFILE",
                "authoritative": True,
                "signals": {"fragile": True, "family": "verniciato"},
            }
        return None

    monkeypatch.setattr(sp.sequence_planner_service, "fetch_station_board", fake_fetch_station_board)
    monkeypatch.setattr(sp, "_get_open_events_by_station", lambda _db: {})
    monkeypatch.setattr(sp, "resolve_article_profile", fake_resolve_article_profile)
    monkeypatch.setattr(sp.sequence_planner_service, "_save", lambda *args, **kwargs: None)
    monkeypatch.setattr(sp.sequence_planner_service, "_agent_monitor", lambda *args, **kwargs: None)

    payload = sp.sequence_planner_service.build_global_sequence(None)
    items = payload.get("items", [])
    by_article = {item["article"]: item for item in items}

    assert by_article["ART-WITH-PROFILE"]["signals"] == {
        "fragile": True,
        "family": "verniciato",
    }
    assert by_article["ART-NO-PROFILE"]["signals"] == {}

