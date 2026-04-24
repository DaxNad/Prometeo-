from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import TLOverviewResponse
from app.services.sequence_planner import sequence_planner_service
from app.api_production import _ensure_tables

router = APIRouter(prefix="/tl", tags=["tl"])


@router.get("/overview", response_model=TLOverviewResponse)
def get_tl_overview(db: Session = Depends(get_db)):
    _ensure_tables(db)

    rows = db.execute(
        text("""
            SELECT
                order_id,
                cliente,
                codice,
                qta,
                postazione,
                stato,
                semaforo,
                due_date,
                note
            FROM board_state
            ORDER BY updated_at DESC, order_id ASC
        """)
    ).mappings().all()

    items = [dict(row) for row in rows]

    urgences = []
    blocked_orders = []
    station_map = {}

    for item in items:
        order_id = str(item.get("order_id") or item.get("codice") or "")
        codice = str(item.get("codice") or "")
        cliente = item.get("cliente")
        postazione = item.get("postazione")
        stato = str(item.get("stato") or "").strip()
        semaforo = str(item.get("semaforo") or "").strip().upper()
        due_date = item.get("due_date")
        note = item.get("note")

        is_blocked = stato.lower() == "bloccato" or semaforo == "ROSSO"

        if is_blocked:
            blocked_orders.append({
                "order_id": order_id,
                "codice": codice,
                "motivo_blocco": note or "stato bloccato o semaforo rosso",
                "postazione": postazione,
                "stato": stato,
                "note": note,
            })

        if semaforo == "ROSSO":
            urgences.append({
                "order_id": order_id,
                "codice": codice,
                "cliente": cliente,
                "due_date": due_date,
                "priority_reason": "semaforo scadenza rosso",
                "stato": stato,
                "postazione": postazione,
            })

        if postazione:
            if postazione not in station_map:
                station_map[postazione] = {
                    "station": postazione,
                    "active_orders": 0,
                    "blocked_orders": 0,
                }

            station_map[postazione]["active_orders"] += 1

            if is_blocked:
                station_map[postazione]["blocked_orders"] += 1

    critical_stations = []

    for station in station_map.values():
        load_level = "BASSO"

        if station["active_orders"] >= 5:
            load_level = "ALTO"
        elif station["active_orders"] >= 3:
            load_level = "MEDIO"

        if station["blocked_orders"] > 0:
            load_level = "CRITICO"

        station["load_level"] = load_level
        critical_stations.append(station)

    sequence_payload = sequence_planner_service.build_global_sequence(db)
    sequence_items = sequence_payload.get("items", [])

    suggested_sequence = []

    for index, item in enumerate(sequence_items[:10], start=1):
        codice = str(item.get("article") or item.get("codice") or "")
        order_id = str(item.get("order_id") or codice or index)
        station = item.get("critical_station") or item.get("station") or item.get("postazione")
        motivo = item.get("explain") or item.get("reason") or item.get("status") or "sequenza planner"

        suggested_sequence.append({
            "position": index,
            "order_id": order_id,
            "codice": codice,
            "station": station,
            "motivo": str(motivo),
        })

    shift_action = None

    if blocked_orders:
        first = blocked_orders[0]
        shift_action = {
            "title": "Sbloccare ordine critico",
            "description": f"Verificare {first.get('codice')} su {first.get('postazione')}. Motivo: {first.get('motivo_blocco')}",
            "target_station": first.get("postazione"),
            "target_order_id": first.get("order_id"),
        }
    elif any(s.get("load_level") == "CRITICO" for s in critical_stations):
        first = sorted(
            [s for s in critical_stations if s.get("load_level") == "CRITICO"],
            key=lambda x: -int(x.get("active_orders", 0)),
        )[0]
        shift_action = {
            "title": "Presidiare postazione critica",
            "description": f"Controllare {first.get('station')}: {first.get('active_orders')} ordini attivi, {first.get('blocked_orders')} bloccati.",
            "target_station": first.get("station"),
            "target_order_id": None,
        }
    elif suggested_sequence:
        first = suggested_sequence[0]
        shift_action = {
            "title": "Lanciare prossimo ordine",
            "description": f"Avviare {first.get('codice')} su {first.get('station')}.",
            "target_station": first.get("station"),
            "target_order_id": first.get("order_id"),
        }

    return TLOverviewResponse(
        generated_at=datetime.utcnow(),
        urgences=urgences,
        blocked_orders=blocked_orders,
        critical_stations=critical_stations,
        suggested_sequence=suggested_sequence,
        shift_action=shift_action,
    )
