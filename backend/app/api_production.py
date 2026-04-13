import json
from datetime import date, datetime
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from .agent_runtime.runtime_hook import trigger_runtime_analysis
from .db.session import get_db
from .services.sequence_planner import sequence_planner_service
from .services.sequence_explain import explain_global_sequence
from .services.explainability import build_tl_explanation
from .smf.smf_adapter import SMFAdapter
from .station_normalizer import normalize_station

router = APIRouter(prefix="/production", tags=["production"])
smf_adapter = SMFAdapter()
SMF_MUTABLE_ORDER_COLUMNS = (
    "Cliente",
    "Codice",
    "Q.ta",
    "Postazione assegnata",
    "Stato (da fare/in corso/finito)",
    "Progress %",
    "Semaforo scadenza",
    "Data richiesta cliente",
    "Note",
    "Priorità",
)


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


def _build_smf_order_row(
    *,
    order_id: str,
    cliente: str,
    codice: str,
    qta: float,
    postazione: str,
    stato: str,
    progress: float,
    semaforo: str,
    due_date: str,
    note: str,
    priority: str,
) -> dict[str, Any]:
    return {
        "ID ordine": order_id,
        "Cliente": cliente,
        "Codice": codice,
        "Q.ta": qta,
        "Postazione assegnata": postazione,
        "Stato (da fare/in corso/finito)": stato,
        "Progress %": progress,
        "Semaforo scadenza": semaforo,
        "Data richiesta cliente": due_date,
        "Note": note,
        "Priorità": priority,
    }


def _build_smf_order_updates(
    *,
    cliente: str,
    codice: str,
    qta: float,
    postazione: str,
    stato: str,
    progress: float,
    semaforo: str,
    due_date: str,
    note: str,
    priority: str,
) -> dict[str, Any]:
    row = _build_smf_order_row(
        order_id="",
        cliente=cliente,
        codice=codice,
        qta=qta,
        postazione=postazione,
        stato=stato,
        progress=progress,
        semaforo=semaforo,
        due_date=due_date,
        note=note,
        priority=priority,
    )
    return {
        key: value
        for key, value in row.items()
        if key in SMF_MUTABLE_ORDER_COLUMNS
    }


def _ensure_tables(db: Session) -> None:
    statements = [
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
        try:
            db.execute(text(stmt))
        except Exception:
            # DDL PostgreSQL-specific (BIGSERIAL, TIMESTAMPTZ, JSONB) non
            # supportato da SQLite in sviluppo/test: ignora e prosegui.
            db.rollback()

    db.commit()


def _build_machine_load(db: Session) -> dict[str, Any]:
    _ensure_tables(db)

    try:
        board_rows = db.execute(
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
    except Exception:
        # board_state non disponibile in sviluppo/test su SQLite
        db.rollback()
        board_rows = []

    try:
        event_rows = db.execute(
            text(
                """
                SELECT
                    station AS postazione,
                    COUNT(*) AS open_events_total,
                    STRING_AGG(title, ' | ' ORDER BY opened_at DESC) AS event_titles
                FROM events
                WHERE status = 'OPEN'
                GROUP BY station
                """
            )
        ).mappings().all()
    except Exception:
        # relazione 'events' non disponibile: fallback safe
        event_rows = []

    board_by_station: dict[str, dict[str, Any]] = {}
    for row in board_rows:
        station = normalize_station(row["postazione"])
        board_by_station[station] = {
            "station": station,
            "orders_total": int(row["orders_total"] or 0),
            "blocked_total": int(row["blocked_total"] or 0),
            "red_total": int(row["red_total"] or 0),
            "yellow_total": int(row["yellow_total"] or 0),
            "green_total": int(row["green_total"] or 0),
            "quantity_total": float(row["quantity_total"] or 0),
            "open_events_total": 0,
            "event_titles": "",
        }

    for row in event_rows:
        station = normalize_station(row["postazione"])
        open_events_total = int(row["open_events_total"] or 0)
        event_titles = str(row["event_titles"] or "")

        if station not in board_by_station:
            board_by_station[station] = {
                "station": station,
                "orders_total": 0,
                "blocked_total": 0,
                "red_total": 0,
                "yellow_total": 0,
                "green_total": 0,
                "quantity_total": 0.0,
                "open_events_total": 0,
                "event_titles": "",
            }

        board_by_station[station]["open_events_total"] += open_events_total
        board_by_station[station]["blocked_total"] += open_events_total
        board_by_station[station]["red_total"] += open_events_total

        if event_titles:
            existing_titles = board_by_station[station]["event_titles"]
            board_by_station[station]["event_titles"] = (
                f"{existing_titles} | {event_titles}" if existing_titles else event_titles
            )

    items = sorted(board_by_station.values(), key=lambda x: x["station"])

    warnings = []
    active_event_stations = [item["station"] for item in items if item["open_events_total"] > 0]
    if active_event_stations:
        warnings.append(
            f"postazioni con segnalazioni operative aperte: {', '.join(active_event_stations)}"
        )

    return {
        "planner_stage": "MACHINE_LOAD_EVENT_AWARE",
        "source": "board_state+events",
        "items_count": len(items),
        "items": items,
        "warnings": warnings,
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

    try:
        existing_order = db.execute(
            text(
                """
                SELECT 1
                FROM production_orders
                WHERE order_id = :order_id
                LIMIT 1
                """
            ),
            {"order_id": order_id},
        ).first()
    except Exception:
        # production_orders non disponibile (SQLite dev/test): tratta come nuovo ordine
        db.rollback()
        existing_order = None

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
                updated_at = CURRENT_TIMESTAMP
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

    production_event_payload = json.dumps({
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
        "station_load": station_load,
        "shared_component_pressure": shared_component_pressure,
        "multi_order_dependency": multi_order_dependency,
        "cluster_saturation": cluster_saturation,
        "station_queue_pressure": station_queue_pressure,
        "note": note,
    }, ensure_ascii=False)

    try:
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
    except Exception:
        # production_events o JSONB non disponibile (SQLite dev/test): ignora
        db.rollback()

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

    smf_sync: dict[str, Any]
    if smf_adapter.available():
        try:
            if existing_order is None:
                smf_sync = {
                    "mode": "append_order",
                    **smf_adapter.append_order(
                        _build_smf_order_row(
                            order_id=order_id,
                            cliente=cliente,
                            codice=codice,
                            qta=qta,
                            postazione=postazione,
                            stato=stato,
                            progress=progress,
                            semaforo=semaforo,
                            due_date=due_date,
                            note=note,
                            priority=priority,
                        )
                    ),
                }
            else:
                smf_sync = {
                    "mode": "update_order",
                    **smf_adapter.update_order(
                        order_id,
                        _build_smf_order_updates(
                            cliente=cliente,
                            codice=codice,
                            qta=qta,
                            postazione=postazione,
                            stato=stato,
                            progress=progress,
                            semaforo=semaforo,
                            due_date=due_date,
                            note=note,
                            priority=priority,
                        ),
                    ),
                }
        except Exception as exc:
            smf_sync = {
                "ok": False,
                "mode": "append_order" if existing_order is None else "update_order",
                "error": f"{exc.__class__.__name__}: {exc}",
            }
    else:
        smf_sync = {"ok": False, "mode": "smf_unavailable"}

    total_rows = db.execute(
        text("SELECT COUNT(*) AS total FROM board_state")
    ).mappings().first()

    return {
        "ok": True,
        "order_id": order_id,
        "rows": int(total_rows["total"]) if total_rows else 0,
        "smf_sync": smf_sync,
    }


@router.get("/board")
def get_board_compat(db: Session = Depends(get_db)):
    return get_board(db)


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

    items = [dict(row) for row in rows]

    trigger_runtime_analysis(
        source="production_board_state",
        line_id="production",
        event_type="board_state_requested",
        severity="info",
        payload={
            "event_domain": "board_state",
            "count": len(items),
        },
    )

    return {
        "ok": True,
        "count": len(items),
        "items": items,
    }


@router.get("/sequence-compat-check")
def get_sequence_compat_check(db: Session = Depends(get_db)):
    return get_sequence(db)


@router.get("/sequence")
def get_sequence(db: Session = Depends(get_db)):
    payload = sequence_planner_service.build_global_sequence(db)

    trigger_runtime_analysis(
        source="production_sequence",
        line_id="planner",
        event_type="sequence_requested",
        severity="info",
        payload={
            "event_domain": "sequence",
            "planner_stage": payload.get("planner_stage"),
            "source": payload.get("source_view"),
            "items_count": payload.get("items_count", 0),
        },
    )

    return {
        "ok": True,
        "planner_stage": payload.get("planner_stage"),
        "source": payload.get("source_view"),
        "items_count": payload.get("items_count", 0),
        "items": payload.get("items", []),
        "warnings": [],
    }


@router.get("/sequence/explain")
def get_sequence_explain(db: Session = Depends(get_db)):
    """Endpoint diagnostico: restituisce la sequenza con spiegazioni
    post‑hoc per ogni item (senza modificare l'architettura del planner).
    Non espone tracebacks completi: in caso di errore ritorna un messaggio sintetico.
    """
    try:
        payload = sequence_planner_service.build_global_sequence(db)
        explained = explain_global_sequence(payload)
        return {
            "ok": True,
            "planner_stage": explained.get("planner_stage"),
            "source": explained.get("source_view"),
            "items_count": explained.get("items_count", 0),
            "items": explained.get("items", []),
            "explainable": explained.get("explainable", True),
        }
    except Exception as exc:
        # Risposta sobria, senza leak del traceback completo
        return {"ok": False, "error": f"sequence_explain_failed: {exc.__class__.__name__}"}


@router.get("/turn-plan")
def get_turn_plan(db: Session = Depends(get_db)):
    payload = sequence_planner_service.build_turn_plan(db)

    trigger_runtime_analysis(
        source="production_turn_plan",
        line_id="planner",
        event_type="turn_plan_requested",
        severity="info",
        payload={
            "event_domain": "turn_plan",
            "planner_stage": payload.get("planner_stage"),
            "source": payload.get("source"),
            "plan_date": payload.get("plan_date"),
            "rotation_logic": payload.get("rotation_logic"),
            "clusters_count": payload.get("clusters_count", 0),
            "assignments_count": payload.get("assignments_count", 0),
        },
    )

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


@router.get("/load")
def get_load_compat(db: Session = Depends(get_db)):
    return get_machine_load(db)


@router.get("/machine-load")
def get_machine_load(db: Session = Depends(get_db)):
    payload = _build_machine_load(db)

    trigger_runtime_analysis(
        source="production_machine_load",
        line_id="production",
        event_type="machine_load_requested",
        severity="info",
        payload={
            "event_domain": "machine_load",
            "planner_stage": payload.get("planner_stage"),
            "source": payload.get("source"),
            "items_count": payload.get("items_count", 0),
            "warnings": payload.get("warnings", []),
        },
    )

    return {
        "ok": True,
        "planner_stage": payload.get("planner_stage"),
        "source": payload.get("source"),
        "items_count": payload.get("items_count", 0),
        "items": payload.get("items", []),
        "warnings": payload.get("warnings", []),
    }


@router.get("/machine_load")
def machine_load_requested(
    db: Session = Depends(get_db),
):
    payload = _build_machine_load(db)
    return {
        "ok": True,
        **payload,
    }


_COMPACT_FIELDS = {"article", "critical_station", "event_impact", "priority_reason", "risk_level", "signals"}


@router.get("/explain")
def get_explain(
    db: Session = Depends(get_db),
    compact: bool = Query(False, description="Se true restituisce solo i campi essenziali per ogni item"),
):
    """Endpoint diagnostico: arricchisce gli item della sequenza
    con priority_reason, risk_level e signals, senza modificare
    il ranking del planner né l'architettura.

    Passa compact=true per ottenere una risposta ridotta (solo
    article, critical_station, event_impact, priority_reason,
    risk_level, signals).
    """
    seq = sequence_planner_service.build_global_sequence(db)
    enriched: list[dict[str, Any]] = []
    for it in seq.get("items", []) or []:
        expl = build_tl_explanation(it)
        full_item = {**it, **expl}
        if compact:
            enriched.append({k: full_item[k] for k in _COMPACT_FIELDS if k in full_item})
        else:
            enriched.append(full_item)

    return {
        "ok": True,
        "planner_stage": seq.get("planner_stage"),
        "source": seq.get("source_view"),
        "items_count": len(enriched),
        "items": enriched,
    }
