from __future__ import annotations

from pydantic import BaseModel


class DomainEvent(BaseModel):
    station: str
    title: str
    status: str
    event_type: str | None = None
    severity: str | None = None

