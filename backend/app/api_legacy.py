import os
import re
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator, model_validator
import psycopg2
from psycopg2.extras import Json

from .db import get_connection
from .schemas import (
    DebugEnvResponse,
    EventCreate,
    EventItem,
    EventMutationResponse,
    EventsResponse,
)

router = APIRouter()

API_BUILD = "events-strong-v5"

ALLOWED_EVENT_KINDS = {
    "OPEN",
    "DONE",
    "ALERT",
    "INFO",
    "BLOCK",
    "QUALITY",
    "MAINT",
    "SYSTEM",
}

ALLOWED_STATUSES = {"OPEN", "DONE"}
ALLOWED_SHIFTS = {"MAT", "POM", "NOT"}
BAD_STRING_VALUES = {"", "string", "null", "none", "undefined"}

STATION_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")


def clean_scalar(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    value = value.strip()
    if value.lower() in BAD_STRING_VALUES:
        return None
    return value


def normalize_station_value(value: Optional[str]) -> Optional[str]:
    value = clean_scalar(value)
    if value is None:
        return None
    value = value.strip().upper().replace("_", "-").replace(" ", "-")
    value = re.sub(r"-{2,}", "-", value)
    return value


def normalize_shift_value(value: Optional[str]) -> Optional[str]:
    value = clean_scalar(value)
    if value is None:
        return None

    value = value.strip().upper()

    mapping = {
        "MATTINA": "MAT",
        "MATT": "MAT",
        "MORNING": "MAT",
        "POMERIGGIO": "POM",
        "POMER": "POM",
        "AFTERNOON": "POM",
        "NOTTE": "NOT",
        "NIGHT": "NOT",
    }

    return mapping.get(value, value)


def normalize_status_value(value: Optional[str]) -> Optional[str]:
    value = clean_scalar(value)
    if value is None:
        return None
    return value.strip().upper()


def is_valid_station(value: str) -> bool:
    return bool(STATION_PATTERN.fullmatch(value))


def clean_payload(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            key = str(k).strip()
            if key in {"additionalProp1", "additionalProp2", "additionalProp3"}:
                continue

            cleaned_value = clean_payload(v)

            if cleaned_value is None:
                continue
            if cleaned_value == "":
                continue
            if cleaned_value == {}:
                continue

            cleaned[key] = cleaned_value
        return cleaned

    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            cleaned_item = clean_payload(item)
            if cleaned_item is None or cleaned_item == "" or cleaned_item == {}:
                continue
            cleaned_list.append(cleaned_item)
        return cleaned_list

    if isinstance(value, str):
        value = value.strip()
        if value.lower() in BAD_STRING_VALUES:
            return None
        return value

    return value


def is_truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        return bool(value)
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def row_to_item(row) -> EventItem:
    return EventItem(
        id=row[0],
        ts=row[1],
        status=row[2],
        title=row[3],
        area=row[4],
        note=row[5],
        code=row[6],
        station=row[7],
        shift=row[8],
        closed_at=row[9],
        kind=row[10],
        payload=row[11] or {},
    )


def generate_event_id() -> str:
    return f"ev-{uuid4().hex[:16]}"


def internal_error(message: str) -> HTTPException:
    return HTTPException(status_code=500, detail=message)


def require_db_connection():
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="Database non configurato o non raggiungibile")
    return conn


def safe_close_connection(conn) -> None:
    if conn is not None:
        conn.close()


class EventCreateStrong(EventCreate):
    @field_validator("id", "code", "operatore", "note", mode="before")
    @classmethod
    def normalize_optional_strings(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            return v
        return clean_scalar(v)

    @field_validator("stato", mode="before")
    @classmethod
    def normalize_stato(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("stato deve essere stringa")
        return normalize_status_value(v)

    @field_validator("turno", mode="before")
    @classmethod
    def normalize_turno(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("turno deve essere stringa")
        return normalize_shift_value(v)

    @field_validator("postazione", mode="before")
    @classmethod
    def normalize_postazione(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("postazione deve essere stringa")
        return normalize_station_value(v)

    @field_validator("kind", mode="before")
    @classmethod
    def normalize_kind(cls, v):
        if v is None:
            raise ValueError("kind obbligatorio")
        if not isinstance(v, str):
            raise ValueError("kind deve essere stringa")
        v = v.strip().upper()
        if v.lower() in BAD_STRING_VALUES or not v:
            raise ValueError("kind non valido")
        return v

    @field_validator("payload", mode="before")
    @classmethod
    def normalize_payload(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("payload deve essere un oggetto JSON")

        payload = clean_payload(v)

        if "station" in payload:
            station_value = payload.get("station")
            if station_value is not None:
                if not isinstance(station_value, str):
                    raise ValueError("payload.station deve essere stringa")
                payload["station"] = normalize_station_value(station_value)

        if "shift" in payload:
            shift_value = payload.get("shift")
            if shift_value is not None:
                if not isinstance(shift_value, str):
                    raise ValueError("payload.shift deve essere stringa")
                payload["shift"] = normalize_shift_value(shift_value)

        if "status" in payload:
            status_value = payload.get("status")
            if status_value is not None:
                if not isinstance(status_value, str):
                    raise ValueError("payload.status deve essere stringa")
                payload["status"] = normalize_status_value(status_value)

        if "operator" in payload:
            operator_value = payload.get("operator")
            if operator_value is not None and not isinstance(operator_value, str):
                raise ValueError("payload.operator deve essere stringa")

        if "operatore" in payload:
            operatore_value = payload.get("operatore")
            if operatore_value is not None and not isinstance(operatore_value, str):
                raise ValueError("payload.operatore deve essere stringa")

        return payload

    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.kind not in ALLOWED_EVENT_KINDS:
            raise ValueError(
                f"kind non ammesso. Valori ammessi: {', '.join(sorted(ALLOWED_EVENT_KINDS))}"
            )

        if self.stato is not None and self.stato not in ALLOWED_STATUSES:
            raise ValueError(
                f"stato non ammesso. Valori ammessi: {', '.join(sorted(ALLOWED_STATUSES))}"
            )

        if self.turno is not None and self.turno not in ALLOWED_SHIFTS:
            raise ValueError(
                f"turno non ammesso. Valori ammessi: {', '.join(sorted(ALLOWED_SHIFTS))}"
            )

        payload_station = self.payload.get("station")
        payload_shift = self.payload.get("shift")
        payload_status = self.payload.get("status")
        payload_title = self.payload.get("title")

        if payload_shift is not None and payload_shift not in ALLOWED_SHIFTS:
            raise ValueError(
                f"payload.shift non ammesso. Valori ammessi: {', '.join(sorted(ALLOWED_SHIFTS))}"
            )

        if payload_status is not None and payload_status not in ALLOWED_STATUSES:
            raise ValueError(
                f"payload.status non ammesso. Valori ammessi: {', '.join(sorted(ALLOWED_STATUSES))}"
            )

        if self.postazione and not is_valid_station(self.postazione):
            raise ValueError(
                "postazione non valida. Esempi ammessi: HENN, ZAW-2, LAV-01, PIDMILL, CP"
            )

        if payload_station and not is_valid_station(payload_station):
            raise ValueError(
                "payload.station non valida. Esempi ammessi: HENN, ZAW-2, LAV-01, PIDMILL, CP"
            )

        if self.kind in {"OPEN", "DONE", "BLOCK", "QUALITY"}:
            if not (self.code or self.postazione or payload_station):
                raise ValueError(
                    "Per OPEN/DONE/BLOCK/QUALITY devi valorizzare almeno code o postazione/station"
                )

        if payload_title is not None and not isinstance(payload_title, str):
            raise ValueError("payload.title deve essere stringa")

        return self


class EventCloseRequest(BaseModel):
    event_id: str

    @field_validator("event_id", mode="before")
    @classmethod
    def normalize_event_id(cls, v):
        if v is None:
            raise ValueError("event_id obbligatorio")
        if not isinstance(v, str):
            raise ValueError("event_id deve essere stringa")
        value = clean_scalar(v)
        if not value:
            raise ValueError("event_id non valido")
        return value


class KpiStationItem(BaseModel):
    station: str
    open: int
    closed: int
    total: int


class KpiStationsResponse(BaseModel):
    ok: bool
    api_build: str
    items: list[KpiStationItem]


@router.get("/debug/env", response_model=DebugEnvResponse)
def debug_env():
    if not is_truthy(os.getenv("APP_DEBUG_ENDPOINTS", "false")):
        raise HTTPException(status_code=404, detail="endpoint non disponibile")

    db_url = os.getenv("DATABASE_URL", "")
    return {
        "ok": True,
        "api_build": API_BUILD,
        "DATABASE_URL_present": bool(db_url),
        "DATABASE_URL_prefix": db_url.split("://")[0] if "://" in db_url else None,
        "PORT": os.getenv("PORT"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_PROJECT_NAME": os.getenv("RAILWAY_PROJECT_NAME"),
        "RAILWAY_SERVICE_NAME": os.getenv("RAILWAY_SERVICE_NAME"),
    }


@router.get("/events", response_model=EventsResponse)
def get_events(
    limit: int = Query(default=100, ge=1, le=500),
    status: Optional[str] = None,
    station: Optional[str] = None,
    code: Optional[str] = None,
    kind: Optional[str] = None,
    shift: Optional[str] = None,
    open_only: bool = False,
):
    conn = None
    cur = None
    try:
        conn = require_db_connection()
        cur = conn.cursor()

        where_clauses = []
        params = []

        if open_only and status:
            status = normalize_status_value(status)
            if status != "OPEN":
                raise HTTPException(
                    status_code=422,
                    detail="open_only=true è compatibile solo con status=OPEN o status assente",
                )

        if open_only:
            where_clauses.append("status = %s")
            params.append("OPEN")

        if status and not open_only:
            status = normalize_status_value(status)
            if status not in ALLOWED_STATUSES:
                raise HTTPException(status_code=422, detail="status filtro non valido")
            where_clauses.append("status = %s")
            params.append(status)

        if station:
            station = normalize_station_value(station)
            if not station or not is_valid_station(station):
                raise HTTPException(status_code=422, detail="station filtro non valida")
            where_clauses.append("station = %s")
            params.append(station)

        if code:
            code = clean_scalar(code)
            if not code:
                raise HTTPException(status_code=422, detail="code filtro non valido")
            where_clauses.append("code = %s")
            params.append(code)

        if kind:
            kind = kind.strip().upper()
            if kind not in ALLOWED_EVENT_KINDS:
                raise HTTPException(status_code=422, detail="kind filtro non valido")
            where_clauses.append("kind = %s")
            params.append(kind)

        if shift:
            shift = normalize_shift_value(shift)
            if shift not in ALLOWED_SHIFTS:
                raise HTTPException(status_code=422, detail="shift filtro non valido")
            where_clauses.append("shift = %s")
            params.append(shift)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                id,
                ts,
                status,
                title,
                area,
                note,
                code,
                station,
                shift,
                closed_at,
                kind,
                payload
            FROM events
            {where_sql}
            ORDER BY ts DESC
            LIMIT %s
        """
        params.append(limit)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        items = [row_to_item(row) for row in rows]
        return EventsResponse(items=items, count=len(items), api_build=API_BUILD)

    except HTTPException:
        raise
    except Exception:
        raise internal_error("Lettura eventi fallita")
    finally:
        if cur is not None:
            cur.close()
        safe_close_connection(conn)


@router.post("/events/add", response_model=EventMutationResponse)
def add_event(event: EventCreateStrong):
    conn = None
    cur = None
    try:
        conn = require_db_connection()
        cur = conn.cursor()

        event_id = event.id or generate_event_id()
        payload = dict(event.payload or {})

        if event.operatore is not None:
            payload["operator"] = event.operatore

        status_value = event.stato or payload.get("status")
        if status_value is None:
            status_value = "DONE" if event.kind == "DONE" else "OPEN"
        status_value = normalize_status_value(status_value)

        if status_value not in ALLOWED_STATUSES:
            raise HTTPException(status_code=422, detail="status non valido")

        title_value = payload.get("title", "PROMETEO EVENT")
        area_value = payload.get("area", "PROD")
        note_value = event.note if event.note is not None else payload.get("note")
        code_value = event.code if event.code is not None else payload.get("code")
        station_value = (
            event.postazione if event.postazione is not None else payload.get("station")
        )
        shift_value = event.turno if event.turno is not None else payload.get("shift")
        closed_at_value = payload.get("closed_at")
        kind_value = event.kind.upper()

        if isinstance(title_value, str):
            title_value = title_value.strip() or "PROMETEO EVENT"
        else:
            title_value = "PROMETEO EVENT"

        if isinstance(area_value, str):
            area_value = area_value.strip().upper() or "PROD"
        else:
            area_value = "PROD"

        if isinstance(code_value, str):
            code_value = clean_scalar(code_value)

        if isinstance(note_value, str):
            note_value = clean_scalar(note_value)

        if isinstance(station_value, str):
            station_value = normalize_station_value(station_value)

        if isinstance(shift_value, str):
            shift_value = normalize_shift_value(shift_value)

        if station_value is not None and not is_valid_station(station_value):
            raise HTTPException(status_code=422, detail="station non valida")

        if shift_value is not None and shift_value not in ALLOWED_SHIFTS:
            raise HTTPException(status_code=422, detail="shift non valido")

        cur.execute(
            """
            INSERT INTO events (
                id,
                ts,
                status,
                title,
                area,
                note,
                code,
                station,
                shift,
                closed_at,
                kind,
                payload
            )
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                ts,
                status,
                title,
                area,
                note,
                code,
                station,
                shift,
                closed_at,
                kind,
                payload
            """,
            (
                event_id,
                status_value,
                title_value,
                area_value,
                note_value,
                code_value,
                station_value,
                shift_value,
                closed_at_value,
                kind_value,
                Json(payload),
            ),
        )

        row = cur.fetchone()
        conn.commit()

        return EventMutationResponse(
            ok=True,
            api_build=API_BUILD,
            item=row_to_item(row),
        )

    except psycopg2.errors.UniqueViolation:
        if conn is not None:
            conn.rollback()
        raise HTTPException(status_code=409, detail="ID evento già esistente")
    except HTTPException:
        if conn is not None:
            conn.rollback()
        raise
    except ValueError as e:
        if conn is not None:
            conn.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        if conn is not None:
            conn.rollback()
        raise internal_error("Inserimento evento fallito")
    finally:
        if cur is not None:
            cur.close()
        safe_close_connection(conn)


@router.post("/events/close", response_model=EventMutationResponse)
def close_event(request: EventCloseRequest):
    conn = None
    cur = None
    try:
        conn = require_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE events
            SET
                status = 'DONE',
                closed_at = NOW()
            WHERE id = %s
            RETURNING
                id,
                ts,
                status,
                title,
                area,
                note,
                code,
                station,
                shift,
                closed_at,
                kind,
                payload
            """,
            (request.event_id,),
        )

        row = cur.fetchone()

        if not row:
            conn.rollback()
            raise HTTPException(status_code=404, detail="evento non trovato")

        conn.commit()

        return EventMutationResponse(
            ok=True,
            api_build=API_BUILD,
            item=row_to_item(row),
        )

    except HTTPException:
        if conn is not None:
            conn.rollback()
        raise
    except Exception:
        if conn is not None:
            conn.rollback()
        raise internal_error("Chiusura evento fallita")
    finally:
        if cur is not None:
            cur.close()
        safe_close_connection(conn)


@router.get("/kpi/stations", response_model=KpiStationsResponse)
def kpi_stations():
    conn = None
    cur = None
    try:
        conn = require_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                station,
                COUNT(*) FILTER (WHERE status = 'OPEN') AS open_events,
                COUNT(*) FILTER (WHERE status = 'DONE') AS closed_events,
                COUNT(*) AS total_events
            FROM events
            WHERE station IS NOT NULL AND station <> ''
            GROUP BY station
            ORDER BY total_events DESC, station ASC;
            """
        )

        rows = cur.fetchall()

        items = [
            {
                "station": r[0],
                "open": r[1],
                "closed": r[2],
                "total": r[3],
            }
            for r in rows
        ]

        return {
            "ok": True,
            "api_build": API_BUILD,
            "items": items,
        }

    except HTTPException:
        raise
    except Exception:
        raise internal_error("KPI query fallita")
    finally:
        if cur is not None:
            cur.close()
        safe_close_connection(conn)
