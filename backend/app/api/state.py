from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import get_connection

router = APIRouter(tags=["State"])


class StationState(BaseModel):
    line: str
    station: str
    status: str
    note: str = ""
    updated_at: Optional[str] = None


class StateResponse(BaseModel):
    total: int
    items: list[StationState]


@router.get("/state", response_model=StateResponse)
def get_all_states() -> StateResponse:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                line,
                station,
                status,
                note,
                CASE
                    WHEN closed_at IS NOT NULL THEN closed_at
                    ELSE opened_at
                END AS updated_at
            FROM events
            WHERE id IN (
                SELECT id
                FROM events e2
                WHERE e2.line = events.line
                  AND e2.station = events.station
                ORDER BY datetime(opened_at) DESC
                LIMIT 1
            )
            ORDER BY line, station
            """
        ).fetchall()

    items = [
        StationState(
            line=row["line"],
            station=row["station"],
            status=row["status"],
            note=row["note"] or "",
            updated_at=row["updated_at"],
        )
        for row in rows
    ]

    return StateResponse(total=len(items), items=items)


@router.get("/state/{line}/{station}", response_model=StationState)
def get_station_state(line: str, station: str) -> StationState:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                line,
                station,
                status,
                note,
                CASE
                    WHEN closed_at IS NOT NULL THEN closed_at
                    ELSE opened_at
                END AS updated_at
            FROM events
            WHERE line = ? AND station = ?
            ORDER BY datetime(opened_at) DESC
            LIMIT 1
            """,
            (line, station),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Stato postazione non trovato")

    return StationState(
        line=row["line"],
        station=row["station"],
        status=row["status"],
        note=row["note"] or "",
        updated_at=row["updated_at"],
    )
