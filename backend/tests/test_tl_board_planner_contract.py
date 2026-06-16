from datetime import date

from fastapi.testclient import TestClient

import app.services.sequence_planner as sequence_planner_module
from app.main import app
from app.services.sequence_planner import sequence_planner_service


def test_production_sequence_preserves_tl_board_minimum_contract(monkeypatch):
    """
    Contract guard: TL Board depends on /production/sequence exposing a stable
    minimum set of fields. This test prevents backend planner changes from
    silently degrading the TL Board table, filters, badges, and detail flow.
    """

    def fake_fetch_station_board(db_sess, view_name: str):
        return [
            {
                "priorita_operativa": 1,
                "articolo": "12063",
                "componenti_condivisi": "468728|468765",
                "quantita": 80,
                "data_spedizione": date(2026, 3, 28),
                "priorita_cliente": "ALTA",
                "complessivo_articolo": "12063",
                "postazione_critica": "ZAW-1",
                "azione_tl": "AVVIO_IMMEDIATO",
                "origine_logica": view_name,
            }
        ]

    monkeypatch.setattr(sequence_planner_service, "fetch_station_board", fake_fetch_station_board)
    monkeypatch.setattr(sequence_planner_module, "build_component_usage_from_db", lambda _db: {})
    monkeypatch.setattr(sequence_planner_module, "_get_open_events_by_station", lambda _db: {})
    monkeypatch.setattr(sequence_planner_module, "resolve_article_profile", lambda _article: None)
    monkeypatch.setattr(sequence_planner_service, "_save", lambda *args, **kwargs: None)
    monkeypatch.setattr(sequence_planner_service, "_agent_monitor", lambda *args, **kwargs: None)

    client = TestClient(app)
    response = client.get("/production/sequence", headers={"X-API-Key": "prometeo-local-key"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["ok"] is True
    assert payload["items_count"] >= 1

    item = payload["items"][0]

    # TL Board identity/ranking columns
    assert item["article"] == "12063"
    assert item["station_rank"] == 1

    # TL Board visible operational columns
    assert item["critical_station"] == "ZAW-1"
    assert item["customer_priority"] == "ALTA"
    assert item["quantity"] == 80
    assert item["tl_action"] == "AVVIO_IMMEDIATO"

    # TL Board event/risk compatibility fields
    assert "event_impact" in item
    assert "open_events_total" in item
    assert isinstance(item["event_impact"], bool)
    assert isinstance(item["open_events_total"], int)

    # Planner admission fields needed for safe operational interpretation
    assert "planner_eligible" in item
    assert "planner_admitted" in item
    assert "admission_reasons" in item
    assert "human_override_allowed" in item
    assert "planner_admission_rule" in item

    assert isinstance(item["planner_eligible"], bool)
    assert isinstance(item["planner_admitted"], bool)
    assert isinstance(item["admission_reasons"], list)
    assert item["human_override_allowed"] is True

    # Explainability/source fields useful for Pattern Learning and TL traceability
    assert item["logic_origin"]
    assert item["source_view"]
    assert "signals" in item
    assert isinstance(item["signals"], dict)
