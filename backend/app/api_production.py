from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

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

from .agent_runtime.runtime_hook import trigger_runtime_analysis


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
            "payload": (
                "{"
                f"\"order_id\": \"{order_id}\", "
                f"\"cliente\": \"{cliente}\", "
                f"\"codice\": \"{codice}\", "
                f"\"qta\": {qta}, "
                f"\"postazione\": \"{postazione}\", "
                f"\"stato\": \"{stato}\", "
                f"\"progress\": {progress}, "
                f"\"semaforo\": \"{semaforo}\", "
                f"\"due_date\": \"{due_date}\", "
                f"\"note\": \"{note.replace(chr(34), chr(39))}\""
                "}"
            ),
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
                note
            FROM board_state
            ORDER BY updated_at DESC, order_id ASC
            """
        )
    ).mappings().all()

    return {
        "ok": True,
        "count": len(rows),
        "items": [
            {
                "order_id": r["order_id"],
                "cliente": r["cliente"],
                "codice": r["codice"],
                "qta": float(r["qta"]) if r["qta"] is not None else 0.0,
                "postazione": r["postazione"],
                "stato": r["stato"],
                "progress": float(r["progress"]) if r["progress"] is not None else 0.0,
                "semaforo": r["semaforo"],
                "due_date": r["due_date"] or "",
                "note": r["note"] or "",
            }
            for r in rows
        ],
    }

@router.get("/sequence")
def get_sequence(db: Session = Depends(get_db)):
    _ensure_tables(db)

    sequence = sequence_planner_service.build_global_sequence(db)

    return {
        "ok": True,
        "planner_stage": sequence.get("planner_stage"),
        "source_view": sequence.get("source_view"),
        "items_count": sequence.get("items_count", 0),
        "items": sequence.get("items", []),
    }

@router.get("/turn-plan")
def get_turn_plan(db: Session = Depends(get_db)):
    _ensure_tables(db)

    plan = sequence_planner_service.build_turn_plan(db)

    return {
        "ok": True,
        "planner_stage": plan.get("planner_stage"),
        "source": plan.get("source"),
        "assignments_count": plan.get("assignments_count", 0),
        "assignments": plan.get("assignments", []),
    }



@router.get("/machine-load")
def get_machine_load(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT
                station,
                SUM(total_cycles) AS total_cycles
            FROM vw_machine_load_summary
            GROUP BY station
            ORDER BY station
            """
        )
    ).mappings().all()

    return {
        "ok": True,
        "items": [
            {
                "station": r["station"],
                "total_cycles": float(r["total_cycles"] or 0),
            }
            for r in rows
        ],
    }
