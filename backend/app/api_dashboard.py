from __future__ import annotations

import os
from datetime import date, datetime

from fastapi import APIRouter

from .db.session import SessionLocal
from .services.sequence_planner import sequence_planner_service
from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/production", tags=["production-dashboard"])

adapter = SMFAdapter()


def _orders_payload() -> dict:
    payload = adapter.preview(sheet="Pianificazione", rows=5000)
    rows_preview = payload.get("rows_preview") or []
    payload["exists"] = bool(payload.get("exists", False)) or bool(rows_preview)
    return payload


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


def _semaforo_from_due(due_raw: str) -> str:
    if not due_raw:
        return ""
    try:
        due = datetime.strptime(str(due_raw).split("T")[0], "%Y-%m-%d").date()
    except Exception:
        return ""
    today = date.today()
    delta = (due - today).days
    if delta < 0:
        return "ROSSO"
    if delta <= 1:
        return "GIALLO"
    return "VERDE"


def _fallback_board_rows() -> list[dict]:
    db = SessionLocal()
    try:
        sequence = sequence_planner_service.build_global_sequence(db) or {}
        items = sequence.get("items") or []
    except Exception:
        items = []
    finally:
        db.close()

    board: list[dict] = []
    for x in items:
        due = x.get("due_date", "")
        board.append(
            {
                "order_id": x.get("article", ""),
                "cliente": "",
                "codice": x.get("article", ""),
                "qta": x.get("quantity", ""),
                "postazione": x.get("critical_station", ""),
                "stato": x.get("tl_action", "AVVIO_IMMEDIATO"),
                "progress": "",
                "semaforo": _semaforo_from_due(due),
                "due_date": due,
                "note": f"auto/sequence ({x.get('logic_origin','')})",
            }
        )
    return board


def _fallback_load_items(board_rows: list[dict]) -> list[dict]:
    load_map: dict[str, dict] = {}
    for row in board_rows:
        station = str(row.get("postazione", "")).strip() or "NON_ASSEGNATA"
        semaforo = str(row.get("semaforo", "")).strip().upper()

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
        load_map[station]["orders_open"] += 1

        if semaforo == "ROSSO":
            load_map[station]["red"] += 1
        elif semaforo == "GIALLO":
            load_map[station]["yellow"] += 1
        elif semaforo == "VERDE":
            load_map[station]["green"] += 1

    return sorted(load_map.values(), key=lambda x: x["postazione"])


@router.get("/board")
def production_board():
    payload = _orders_payload()
    rows = _filtered_rows()

    if payload.get("exists") and rows:
        board: list[dict] = []
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
        return {"ok": True, "count": len(board), "items": board}

    board = _fallback_board_rows()
    return {"ok": True, "count": len(board), "items": board}


@router.get("/delays")
def production_delays():
    payload = _orders_payload()
    rows = _filtered_rows()

    if payload.get("exists") and rows:
        delayed: list[dict] = []
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
        return {"ok": True, "count": len(delayed), "items": delayed}

    board = _fallback_board_rows()
    delayed = [row for row in board if str(row.get("semaforo", "")).upper() in {"ROSSO", "GIALLO"}]
    items = [
        {
            "order_id": row.get("order_id", ""),
            "codice": row.get("codice", ""),
            "cliente": row.get("cliente", ""),
            "postazione": row.get("postazione", ""),
            "stato": row.get("stato", ""),
            "progress": row.get("progress", ""),
            "semaforo": row.get("semaforo", ""),
            "due_date": row.get("due_date", ""),
        }
        for row in delayed
    ]
    return {"ok": True, "count": len(items), "items": items}


@router.get("/load")
def production_load():
    payload = _orders_payload()
    rows = _filtered_rows()

    if payload.get("exists") and rows:
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
        return {"ok": True, "count": len(items), "items": items}

    board = _fallback_board_rows()
    items = _fallback_load_items(board)
    return {"ok": True, "count": len(items), "items": items}
