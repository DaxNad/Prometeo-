from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..repositories.factory import get_events_repository

router = APIRouter(tags=["State"])


class StationState(BaseModel):
    line: str
    station: str
    status: str
    severity: Optional[str] = None
    event_type: Optional[str] = None
    title: Optional[str] = None
    note: str = ""
    source: Optional[str] = None
    event_id: Optional[str] = None
    updated_at: Optional[str] = None
    priority_score: int = 0


class StateResponse(BaseModel):
    total: int
    items: list[StationState]


def _to_state(item: dict) -> StationState:
    return StationState(
        line=item["line"],
        station=item["station"],
        status=item["status"],
        severity=item.get("severity"),
        event_type=item.get("event_type"),
        title=item.get("title"),
        note=item.get("note") or "",
        source=item.get("source"),
        event_id=item.get("event_id"),
        updated_at=str(item["updated_at"]) if item.get("updated_at") is not None else None,
        priority_score=int(item.get("priority_score") or 0),
    )


@router.get("/state", response_model=StateResponse)
def get_all_states() -> StateResponse:
    repo = get_events_repository()
    items = [_to_state(item) for item in repo.list_station_states()]
    return StateResponse(total=len(items), items=items)


@router.get("/state/{line}/{station}", response_model=StationState)
def get_station_state(line: str, station: str) -> StationState:
    repo = get_events_repository()
    item = repo.get_station_state(line, station)
    if item is None:
        raise HTTPException(status_code=404, detail="Stato postazione non trovato")
    return _to_state(item)
