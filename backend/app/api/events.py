from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..repositories.factory import get_events_repository

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


class BulkCloseByLine(BaseModel):
    line: str = Field(min_length=1)
    closed_by: str = "dashboard"


class EventListResponse(BaseModel):
    total: int
    open_count: int
    closed_count: int
    items: list[Event]


class BulkCloseResponse(BaseModel):
    line: str
    closed_count: int
    closed_ids: list[str]


def _to_event(item: dict) -> Event:
    return Event(
        id=item["id"],
        title=item["title"],
        line=item["line"],
        station=item["station"],
        event_type=item["event_type"],
        severity=item["severity"],
        status=item["status"],
        note=item.get("note") or "",
        source=item.get("source") or "manual",
        opened_at=str(item["opened_at"]),
        closed_at=str(item["closed_at"]) if item.get("closed_at") is not None else None,
        closed_by=item.get("closed_by"),
    )


@router.get("/events", response_model=EventListResponse)
def list_events() -> EventListResponse:
    repo = get_events_repository()
    rows = repo.list_events()
    items = [_to_event(row) for row in rows]
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
    repo = get_events_repository()
    rows = repo.list_active_events()
    items = [_to_event(row) for row in rows]

    return EventListResponse(
        total=len(items),
        open_count=len(items),
        closed_count=0,
        items=items,
    )


@router.post("/events/create", response_model=Event)
def create_event(payload: EventCreate) -> Event:
    repo = get_events_repository()
    try:
        item = repo.create_event(payload.model_dump())
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return _to_event(item)


@router.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str) -> Event:
    repo = get_events_repository()
    item = repo.get_event(event_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return _to_event(item)


@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, payload: EventUpdate) -> Event:
    repo = get_events_repository()
    try:
        item = repo.update_event(event_id, payload.model_dump(exclude_unset=True))
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    if item is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return _to_event(item)


@router.post("/events/{event_id}/close", response_model=Event)
def close_event(event_id: str, payload: EventClose = EventClose()) -> Event:
    repo = get_events_repository()
    try:
        item = repo.close_event(event_id, payload.closed_by)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    if item is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return _to_event(item)


@router.post("/events/close-by-line", response_model=BulkCloseResponse)
def close_events_by_line(payload: BulkCloseByLine) -> BulkCloseResponse:
    repo = get_events_repository()
    try:
        result = repo.close_events_by_line(payload.line.strip(), payload.closed_by)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    return BulkCloseResponse(**result)
