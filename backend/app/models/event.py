from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


EventStatus = Literal["OPEN", "CLOSED"]
EventSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    line: str
    station: str
    event_type: str
    severity: EventSeverity = "MEDIUM"
    status: EventStatus = "OPEN"
    note: Optional[str] = None
    source: Optional[str] = "manual"
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    closed_by: Optional[str] = None


class EventCreate(BaseModel):
    title: str
    line: str
    station: str
    event_type: str
    severity: EventSeverity = "MEDIUM"
    note: Optional[str] = None
    source: Optional[str] = "manual"


class EventClose(BaseModel):
    closed_by: Optional[str] = "system"
    note: Optional[str] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    line: Optional[str] = None
    station: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[EventSeverity] = None
    note: Optional[str] = None
    source: Optional[str] = None


class EventListResponse(BaseModel):
    total: int
    open_count: int
    closed_count: int
    items: list[Event]
