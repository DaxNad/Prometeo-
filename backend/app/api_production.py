from datetime import date, datetime
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from .agent_runtime.runtime_hook import trigger_runtime_analysis
from .db.session import get_db
from .services.sequence_planner import sequence_planner_service

router = APIRouter(prefix="/production", tags=["production"])


def _normalize_stato(value: Any) -> str:
    if value is None:
        return "da fare"
    s = str(value).strip().lower()
    if not s:
        return "da fare"
    return s


def _progress_from_stato(stato: str) -> float:
    mapping = {
        "da fare": 0.0,
        "in corso": 50.0,
        "finito": 100.0,
        "bloccato": 0.0,
    }
    return mapping.get(stato, 0.0)


def _semaforo_from_stato(stato: str) -> str:
    mapping = {
        "da fare": "GIALLO",
        "in corso": "GIALLO",
        "finito": "VERDE",
        "bloccato": "ROSSO",
    }
    return mapping.get(stato, "GIALLO")


def _safe_json_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace(chr(34), chr(39))


def _parse_due_date(value: Any) -> date | None:
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def _is_overdue(due_date_value: str, stato: str, semaforo: str) -> bool:
    stato_norm = str(stato).strip().lower()
    if stato_norm == "finito":
        return False

    if str(semaforo).strip().upper() == "ROSSO":
        return True

    parsed = _parse_due_date(due_date_value)
    if parsed is None:
        return False

    return parsed < date.today()


def _is_blocked(stato: str, semaforo: str) -> bool:
    if str(stato).strip().lower() == "bloccato":
        return True
    return str(semaforo).strip().upper() == "ROSSO"


def _ensure_tables(db: Session) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS production_orders (
            id BIGSERIAL PRIMARY KEY,
            order_id TEXT NOT NULL UNIQUE,
            cliente TEXT NOT NULL,
            codice TEXT NOT NULL,
            qta NUMERIC(12,2) NOT NULL DEFAULT 0,
            postazione TEXT NOT NULL,
            stato TEXT NOT NULL DEFAULT 'da fare',
            progress NUMERIC(5,2) NOT NULL DEFAULT 0,
            semaforo TEXT NOT NULL DEFAULT 'GIALLO',
            due_date TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS board_state (
            id BIGSERIAL PRIMARY KEY,
            order_id TEXT NOT NULL UNIQUE,
            cliente TEXT NOT NULL,
            codice TEXT NOT NULL,
            qta NUMERIC(12,2) NOT NULL DEFAULT 0,
            postazione TEXT NOT NULL,
            stato TEXT NOT NULL DEFAULT 'da fare',
            progress NUMERIC(5,2) NOT NULL DEFAULT 0,
            semaforo TEXT NOT NULL DEFAULT 'GIALLO',
            due_date TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS production_events (
            id BIGSERIAL PRIMARY KEY,
            order_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_production_orders_order_id
        ON production_orders(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_board_state_order_id
        ON board_state(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_production_events_order_id
        ON production_events(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_production_events_created_at
        ON production_events(created_at DESC)
        """,
    ]

    for stmt in statements:
        db.execute(text(stmt))

    db.commit()


def _build_machine_load(db: Session) -> dict[str, Any]:
    _ensure_tables(db)

    rows = db.execute(
        text(
            """
            SELECT
                postazione,
                COUNT(*) AS orders_total,
                COUNT(*) FILTER (WHERE LOWER(stato) = 'bloccato') AS blocked_total,
                COUNT(*) FILTER (WHERE UPPER(semaforo) = 'ROSSO') AS red_total,
                COUNT(*) FILTER (WHERE UPPER(semaforo) = 'GIALLO') AS yellow_total,
                COUNT(*) FILTER (WHERE UPPER(semaforo) = 'VERDE') AS green_total,
                COALESCE(SUM(qta), 0) AS quantity_total
            FROM board_state
            GROUP BY postazione
            ORDER BY postazione ASC
            """
        )
    ).mappings().all()

    items = []
    for row in rows:
        items.append(
            {
                "station": row["postazione"],
                "orders_total": int(row["orders_total"] or 0),
                "blocked_total": int(row["blocked_total"] or 0),
                "red_total": int(row["red_total"] or 0),
                "yellow_total": int(row["yellow_total"] or 0),
                "green_total": int(row["green_total"] or 0),
                "quantity_total": float(row["quantity_total"] or 0),
            }
        )

    return {
        "planner_stage": "MACHINE_LOAD_BOARD_STATE",
        "source": "board_state",
        "items_count": len(items),
        "items": items,
        "warnings": [],
    }


# ---------------------------------------------------------------------------
# PROMETEO CORE – PRIMARY OPERATIONAL FLOW
#
# Questo modulo rappresenta il punto primario di ingresso per eventi
# di produzione operativi.
#
# Flusso reale:
#   /production/order  →  persist order state
#                     →  write production_events
#                     →  trigger agent_runtime
#
# Il ramo /events/create rimane secondario su questo backend.
#
# Ogni modifica futura al flusso decisionale deve mantenere
# l'hook runtime attivo in questo punto.
# ---------------------------------------------------------------------------


@router.post("/order")
def create_or_update_order(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    _ensure_tables(db)

    order_id = str(payload.get("order_id", "")).strip()
    cliente = str(payload.get("cliente", "")).strip()
    codice = str(payload.get("codice", "")).strip()
    qta = float(payload.get("qta", 0) or 0)
    postazione = str(payload.get("postazione", "")).strip()
    stato = _normalize_stato(payload.get("stato"))
    due_date = str(payload.get("due_date", "") or "")
    note = str(payload.get("note", "") or "")
    progress = float(payload.get("progress", _progress_from_stato(stato)))
    semaforo = str(payload.get("semaforo", _semaforo_from_stato(stato)))

    if not order_id:
        return {"ok": False, "error": "order_id mancante"}
    if not cliente:
        return {"ok": False, "error": "cliente mancante"}
    if not codice:
        return {"ok": False, "error": "codice mancante"}
    if not postazione:
        return {"ok": False, "error": "postazione mancante"}

    blocked = _is_blocked(stato, semaforo)
    overdue = _is_overdue(due_date, stato, semaforo)
    priority = str(payload.get("priority", payload.get("priorita", "")) or "").strip().upper()
    if not priority:
        priority = "ALTA" if str(semaforo).strip().upper() == "ROSSO" else "MEDIA"

    shared_component_pressure = int(payload.get("shared_component_pressure", 0) or 0)
    multi_order_dependency = int(payload.get("multi_order_dependency", 0) or 0)
    cluster_saturation = float(payload.get("cluster_saturation", 0) or 0)
    station_queue_pressure = int(payload.get("station_queue_pressure", 0) or 0)
    station_load = int(payload.get("station_load", station_queue_pressure) or 0)

    db.execute(
        text(
            """
            INSERT INTO production_orders (
                order_id, cliente, codice, qta, postazione, stato,
                progress, semaforo, due_date, note
            )
            VALUES (
                :order_id, :cliente, :codice, :qta, :postazione, :stato,
                :progress, :semaforo, :due_date, :note
            )
            ON CONFLICT (order_id) DO UPDATE SET
                cliente = EXCLUDED.cliente,
                codice = EXCLUDED.codice,
                qta = EXCLUDED.qta,
                postazione = EXCLUDED.postazione,
                stato = EXCLUDED.stato,
                progress = EXCLUDED.progress,
                semaforo = EXCLUDED.semaforo,
                due_date = EXCLUDED.due_date,
                note = EXCLUDED.note,
                updated_at = NOW()
            """
        ),
        {
            "order_id": order_id,
            "cliente": cliente,
            "codice": codice,
            "qta": qta,
            "postazione": postazione,
            "stato": stato,
            "progress": progress,
            "semaforo": semaforo,
            "due_date": due_date,
            "note": note,
        },
    )

    db.execute(
        text(
            """
            INSERT INTO board_state (
                order_id, cliente, codice, qta, postazione, stato,
                progress, semaforo, due_date, note
            )
            VALUES (
                :order_id, :cliente, :codice, :qta, :postazione, :stato,
                :progress, :semaforo, :due_date, :note
            )
            ON CONFLICT (order_id) DO UPDATE SET
                cliente = EXCLUDED.cliente,
                codice = EXCLUDED.codice,
                qta = EXCLUDED.qta,
                postazione = EXCLUDED.postazione,
                stato = EXCLUDED.stato,
                progress = EXCLUDED.progress,
                semaforo = EXCLUDED.semaforo,
                due_date = EXCLUDED.due_date,
                note = EXCLUDED.note,
                updated_at = NOW()
            """
        ),
        {
            "order_id": order_id,
            "cliente": cliente,
            "codice": codice,
            "qta": qta,
            "postazione": postazione,
            "stato": stato,
            "progress": progress,
            "semaforo": semaforo,
            "due_date": due_date,
            "note": note,
        },
    )

    production_event_payload = (
        "{"
        f"\"event_domain\": \"order\", "
        f"\"order_id\": \"{_safe_json_text(order_id)}\", "
        f"\"cliente\": \"{_safe_json_text(cliente)}\", "
        f"\"codice\": \"{_safe_json_text(codice)}\", "
        f"\"qta\": {qta}, "
        f"\"postazione\": \"{_safe_json_text(postazione)}\", "
        f"\"stato\": \"{_safe_json_text(stato)}\", "
        f"\"progress\": {progress}, "
        f"\"semaforo\": \"{_safe_json_text(semaforo)}\", "
        f"\"priority\": \"{_safe_json_text(priority)}\", "
        f"\"due_date\": \"{_safe_json_text(due_date)}\", "
        f"\"blocked\": {str(blocked).lower()}, "
        f"\"overdue\": {str(overdue).lower()}, "
        f"\"station_load\": {station_load}, "
        f"\"shared_component_pressure\": {shared_component_pressure}, "
        f"\"multi_order_dependency\": {multi_order_dependency}, "
        f"\"cluster_saturation\": {cluster_saturation}, "
        f"\"station_queue_pressure\": {station_queue_pressure}, "
        f"\"note\": \"{_safe_json_text(note)}\""
        "}"
    )

    db.execute(
        text(
            """
            INSERT INTO production_events (
                order_id, event_type, payload
            )
            VALUES (
                :order_id,
                :event_type,
                CAST(:payload AS JSONB)
            )
            """
        ),
        {
            "order_id": order_id,
            "event_type": "order_upserted",
            "payload": production_event_payload,
        },
    )

    trigger_runtime_analysis(
        source="production_order_upsert",
        line_id=postazione,
        event_type="order_upserted",
        severity=(
            "low"
            if str(semaforo).strip().upper() == "VERDE"
            else "medium"
            if str(semaforo).strip().upper() == "GIALLO"
            else "high"
        ),
        payload={
            "event_domain": "order",
            "order_id": order_id,
            "cliente": cliente,
            "codice": codice,
            "qta": qta,
            "postazione": postazione,
            "stato": stato,
            "progress": progress,
            "semaforo": semaforo,
            "priority": priority,
            "due_date": due_date,
            "blocked": blocked,
            "overdue": overdue,
            "note": note,
            "station_load": station_load,
            "shared_component_pressure": shared_component_pressure,
            "multi_order_dependency": multi_order_dependency,
            "cluster_saturation": cluster_saturation,
            "station_queue_pressure": station_queue_pressure,
        },
    )

    db.commit()

    total_rows = db.execute(
        text("SELECT COUNT(*) AS total FROM board_state")
    ).mappings().first()

    return {
        "ok": True,
        "order_id": order_id,
        "rows": int(total_rows["total"]) if total_rows else 0,
    }


@router.get("/board-state")
def get_board(db: Session = Depends(get_db)):
    _ensure_tables(db)

    rows = db.execute(
        text(
            """
            SELECT
                order_id,
                cliente,
                codice,
                qta,
                postazione,
                stato,
                progress,
                semaforo,
                due_date,
                note,
                updated_at
            FROM board_state
            ORDER BY updated_at DESC, order_id ASC
            """
        )
    ).mappings().all()

    return {
        "ok": True,
        "count": len(rows),
        "items": [dict(row) for row in rows],
    }

@router.get("/sequence")
def get_sequence(db: Session = Depends(get_db)):
    payload = sequence_planner_service.build_global_sequence(db)
    return {
        "ok": True,
        "planner_stage": payload.get("planner_stage"),
        "source": payload.get("source_view"),
        "items_count": payload.get("items_count", 0),
        "items": payload.get("items", []),
        "warnings": [],
    }


@router.get("/turn-plan")
def get_turn_plan(db: Session = Depends(get_db)):
    payload = sequence_planner_service.build_turn_plan(db)
    return {
        "ok": True,
        "planner_stage": payload.get("planner_stage"),
        "source": payload.get("source"),
        "plan_date": payload.get("plan_date"),
        "rotation_logic": payload.get("rotation_logic"),
        "clusters_count": payload.get("clusters_count", 0),
        "assignments_count": payload.get("assignments_count", 0),
        "items": payload.get("assignments", []),
        "warnings": [],
    }


@router.get("/machine-load")
def get_machine_load(db: Session = Depends(get_db)):
    payload = _build_machine_load(db)
    return {
        "ok": True,
        "planner_stage": payload.get("planner_stage"),
        "source": payload.get("source"),
        "items_count": payload.get("items_count", 0),
        "items": payload.get("items", []),
        "warnings": payload.get("warnings", []),
    }
