from __future__ import annotations

from fastapi import APIRouter

from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/production", tags=["production-dashboard"])

adapter = SMFAdapter()


def _orders_payload() -> dict:
    return adapter.preview(sheet="Pianificazione", rows=5000)


def _is_meaningful_row(row: dict) -> bool:
    order_id = str(row.get("ID ordine", "")).strip()
    codice = str(row.get("Codice", "")).strip()
    cliente = str(row.get("Cliente", "")).strip()
    postazione = str(row.get("Postazione assegnata", "")).strip()
    stato = str(row.get("Stato (da fare/in corso/finito)", "")).strip()
    progress = str(row.get("Progress %", "")).strip()

    return any([order_id, codice, cliente, postazione, stato, progress])


def _filtered_rows() -> list[dict]:
    payload = _orders_payload()
    rows = payload.get("rows_preview", [])
    return [row for row in rows if _is_meaningful_row(row)]


@router.get("/board")
def production_board():
    rows = _filtered_rows()

    board = []
    for row in rows:
        board.append(
            {
                "order_id": row.get("ID ordine", ""),
                "cliente": row.get("Cliente", ""),
                "codice": row.get("Codice", ""),
                "qta": row.get("Q.ta", ""),
                "postazione": row.get("Postazione assegnata", ""),
                "stato": row.get("Stato (da fare/in corso/finito)", ""),
                "progress": row.get("Progress %", ""),
                "semaforo": row.get("Semaforo scadenza", ""),
                "due_date": row.get("Data richiesta cliente", ""),
                "note": row.get("Note", ""),
            }
        )

    return {
        "ok": True,
        "count": len(board),
        "items": board,
    }


@router.get("/delays")
def production_delays():
    rows = _filtered_rows()

    delayed = []
    for row in rows:
        semaforo = str(row.get("Semaforo scadenza", "")).strip().upper()
        if semaforo in {"ROSSO", "GIALLO"}:
            delayed.append(
                {
                    "order_id": row.get("ID ordine", ""),
                    "codice": row.get("Codice", ""),
                    "cliente": row.get("Cliente", ""),
                    "postazione": row.get("Postazione assegnata", ""),
                    "stato": row.get("Stato (da fare/in corso/finito)", ""),
                    "progress": row.get("Progress %", ""),
                    "semaforo": semaforo,
                    "due_date": row.get("Data richiesta cliente", ""),
                }
            )

    return {
        "ok": True,
        "count": len(delayed),
        "items": delayed,
    }


@router.get("/load")
def production_load():
    rows = _filtered_rows()

    load_map: dict[str, dict] = {}

    for row in rows:
        station = str(row.get("Postazione assegnata", "")).strip() or "NON_ASSEGNATA"
        semaforo = str(row.get("Semaforo scadenza", "")).strip().upper()
        stato = str(row.get("Stato (da fare/in corso/finito)", "")).strip().lower()

        if station not in load_map:
            load_map[station] = {
                "postazione": station,
                "orders_total": 0,
                "orders_open": 0,
                "orders_done": 0,
                "red": 0,
                "yellow": 0,
                "green": 0,
            }

        load_map[station]["orders_total"] += 1

        if stato == "finito":
            load_map[station]["orders_done"] += 1
        else:
            load_map[station]["orders_open"] += 1

        if semaforo == "ROSSO":
            load_map[station]["red"] += 1
        elif semaforo == "GIALLO":
            load_map[station]["yellow"] += 1
        elif semaforo == "VERDE":
            load_map[station]["green"] += 1

    items = sorted(load_map.values(), key=lambda x: x["postazione"])

    return {
        "ok": True,
        "count": len(items),
        "items": items,
    }
