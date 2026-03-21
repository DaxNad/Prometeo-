from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import get_connection

router = APIRouter(tags=["Events"])


class Event(BaseModel):
    id: str
    title: str
    line: str
    station: str
    event_type: str
    severity: str
    status: str
    note: str = ""
    source: str = "manual"
    opened_at: str
    closed_at: Optional[str] = None
    closed_by: Optional[str] = None


class EventCreate(BaseModel):
    title: str = Field(min_length=1)
    line: str = Field(min_length=1)
    station: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    note: str = ""
    source: str = "manual"


class EventUpdate(BaseModel):
    title: Optional[str] = None
    line: Optional[str] = None
    station: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = None
    note: Optional[str] = None
    source: Optional[str] = None
    status: Optional[Literal["OPEN", "CLOSED"]] = None


class EventClose(BaseModel):
    closed_by: str = "dashboard"


class EventListResponse(BaseModel):
    total: int
    open_count: int
    closed_count: int
    items: list[Event]


def _row_to_event(row) -> Event:
    return Event(
        id=row["id"],
        title=row["title"],
        line=row["line"],
        station=row["station"],
        event_type=row["event_type"],
        severity=row["severity"],
        status=row["status"],
        note=row["note"] or "",
        source=row["source"] or "manual",
        opened_at=row["opened_at"],
        closed_at=row["closed_at"],
        closed_by=row["closed_by"],
    )


@router.get("/events", response_model=EventListResponse)
def list_events() -> EventListResponse:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM events
            ORDER BY datetime(opened_at) DESC
            """
        ).fetchall()

    items = [_row_to_event(row) for row in rows]
    open_count = sum(1 for item in items if item.status == "OPEN")
    closed_count = sum(1 for item in items if item.status == "CLOSED")

    return EventListResponse(
        total=len(items),
        open_count=open_count,
        closed_count=closed_count,
        items=items,
    )


@router.get("/events/active", response_model=EventListResponse)
def list_active_events() -> EventListResponse:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM events
            WHERE status = 'OPEN'
            ORDER BY datetime(opened_at) DESC
            """
        ).fetchall()

    items = [_row_to_event(row) for row in rows]

    return EventListResponse(
        total=len(items),
        open_count=len(items),
        closed_count=0,
        items=items,
    )


@router.post("/events/create", response_model=Event)
def create_event(payload: EventCreate) -> Event:
    now = datetime.utcnow().isoformat()
    event = Event(
        id=str(uuid4()),
        title=payload.title.strip(),
        line=payload.line.strip(),
        station=payload.station.strip(),
        event_type=payload.event_type.strip(),
        severity=payload.severity,
        status="OPEN",
        note=payload.note.strip(),
        source=payload.source.strip() or "manual",
        opened_at=now,
        closed_at=None,
        closed_by=None,
    )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO events (
                id, title, line, station, event_type, severity, status,
                note, source, opened_at, closed_at, closed_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.title,
                event.line,
                event.station,
                event.event_type,
                event.severity,
                event.status,
                event.note,
                event.source,
                event.opened_at,
                event.closed_at,
                event.closed_by,
            ),
        )
        conn.commit()

    return event


@router.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str) -> Event:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    return _row_to_event(row)


@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, payload: EventUpdate) -> Event:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Evento non trovato")

        current = _row_to_event(row)

        updated = Event(
            id=current.id,
            title=(payload.title.strip() if payload.title is not None else current.title),
            line=(payload.line.strip() if payload.line is not None else current.line),
            station=(payload.station.strip() if payload.station is not None else current.station),
            event_type=(payload.event_type.strip() if payload.event_type is not None else current.event_type),
            severity=(payload.severity if payload.severity is not None else current.severity),
            status=(payload.status if payload.status is not None else current.status),
            note=(payload.note.strip() if payload.note is not None else current.note),
            source=(payload.source.strip() if payload.source is not None else current.source),
            opened_at=current.opened_at,
            closed_at=current.closed_at,
            closed_by=current.closed_by,
        )

        conn.execute(
            """
            UPDATE events
            SET title = ?, line = ?, station = ?, event_type = ?, severity = ?,
                status = ?, note = ?, source = ?, closed_at = ?, closed_by = ?
            WHERE id = ?
            """,
            (
                updated.title,
                updated.line,
                updated.station,
                updated.event_type,
                updated.severity,
                updated.status,
                updated.note,
                updated.source,
                updated.closed_at,
                updated.closed_by,
                updated.id,
            ),
        )
        conn.commit()

    return updated


@router.post("/events/{event_id}/close", response_model=Event)
def close_event(event_id: str, payload: EventClose = EventClose()) -> Event:
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Evento non trovato")

        current = _row_to_event(row)

        if current.status == "CLOSED":
            return current

        conn.execute(
            """
            UPDATE events
            SET status = 'CLOSED',
                closed_at = ?,
                closed_by = ?
            WHERE id = ?
            """,
            (now, payload.closed_by, event_id),
        )
        conn.commit()

        updated_row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

    return _row_to_event(updated_row)
