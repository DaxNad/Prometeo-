from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter

from .db.session import SessionLocal
from .services.sequence_planner import sequence_planner_service
from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/production", tags=["production-dashboard"])

adapter = SMFAdapter()

ACTION_PRIORITY = {
    "AVVIO_IMMEDIATO": 3,
    "PREPARARE_CAMBIO_SERIE": 2,
    "MONITORARE": 1,
}

SEMAFORO_PRIORITY = {
    "ROSSO": 3,
    "GIALLO": 2,
    "VERDE": 1,
    "": 0,
}


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


def _parse_due(due_raw: str):
    if not due_raw:
        return None
    try:
        return datetime.strptime(str(due_raw).split("T")[0], "%Y-%m-%d").date()
    except Exception:
        return None


def _strongest_action(actions: set[str]) -> str:
    if not actions:
        return ""
    return sorted(actions, key=lambda x: ACTION_PRIORITY.get(x, 0), reverse=True)[0]


def _strongest_semaforo(semafori: set[str]) -> str:
    if not semafori:
        return ""
    return sorted(semafori, key=lambda x: SEMAFORO_PRIORITY.get(x, 0), reverse=True)[0]


def _fallback_board_rows() -> list[dict]:
    db = SessionLocal()
    try:
        sequence = sequence_planner_service.build_global_sequence(db) or {}
        items = sequence.get("items") or []
    except Exception:
        items = []
    finally:
        db.close()

    grouped: dict[str, dict] = {}

    for x in items:
        article = str(x.get("article", "")).strip()
        if not article:
            continue

        due = str(x.get("due_date", "")).strip()
        semaforo = _semaforo_from_due(due)
        action = str(x.get("tl_action", "")).strip() or "MONITORARE"
        station = str(x.get("critical_station", "")).strip() or "NON_ASSEGNATA"
        qty = x.get("quantity", 0) or 0
        logic_origin = str(x.get("logic_origin", "")).strip()
        shared_components = [str(c).strip() for c in (x.get("shared_components") or []) if str(c).strip()]

        if article not in grouped:
            grouped[article] = {
                "order_id": article,
                "cliente": "",
                "codice": article,
                "qta": qty,
                "postazione": station,
                "stato": action,
                "progress": "",
                "semaforo": semaforo,
                "due_date": due,
                "_due_obj": _parse_due(due),
                "_actions": {action} if action else set(),
                "_semafori": {semaforo} if semaforo else set(),
                "_stations": {station} if station else set(),
                "_origins": {logic_origin} if logic_origin else set(),
                "_components": set(shared_components),
                "_clusters": 1,
            }
            continue

        row = grouped[article]
        row["_clusters"] += 1
        row["_components"].update(shared_components)
        if logic_origin:
            row["_origins"].add(logic_origin)
        if action:
            row["_actions"].add(action)
        if semaforo:
            row["_semafori"].add(semaforo)
        if station:
            row["_stations"].add(station)

        current_due = row["_due_obj"]
        new_due = _parse_due(due)

        if new_due and (current_due is None or new_due < current_due):
            row["_due_obj"] = new_due
            row["due_date"] = due

        row["qta"] = max(row["qta"], qty)
        row["stato"] = _strongest_action(row["_actions"])
        row["semaforo"] = _strongest_semaforo(row["_semafori"])
        row["postazione"] = sorted(row["_stations"])[0] if row["_stations"] else "NON_ASSEGNATA"

    board: list[dict] = []
    for article, row in grouped.items():
        components = sorted(row["_components"])
        origins = sorted(row["_origins"])
        note_parts = ["auto/sequence consolidato"]
        note_parts.append(f"cluster={row['_clusters']}")
        if origins:
            note_parts.append(f"origini={','.join(origins)}")
        if components:
            note_parts.append(f"componenti={','.join(components)}")

        board.append(
            {
                "order_id": row["order_id"],
                "cliente": row["cliente"],
                "codice": row["codice"],
                "qta": row["qta"],
                "postazione": row["postazione"],
                "stato": row["stato"],
                "progress": row["progress"],
                "semaforo": row["semaforo"],
                "due_date": row["due_date"],
                "note": " | ".join(note_parts),
            }
        )

    def _sort_key(x: dict):
        due_obj = _parse_due(x.get("due_date", "")) or date.max
        return (
            -SEMAFORO_PRIORITY.get(str(x.get("semaforo", "")).upper(), 0),
            due_obj,
            -ACTION_PRIORITY.get(str(x.get("stato", "")).upper(), 0),
            str(x.get("codice", "")),
        )

    return sorted(board, key=_sort_key)


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
