from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    id: Optional[str] = None
    kind: str
    code: Optional[str] = None
    postazione: Optional[str] = None
    stato: Optional[str] = None
    operatore: Optional[str] = None
    turno: Optional[str] = None
    note: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventItem(BaseModel):
    id: str
    ts: Optional[datetime] = None
    status: Optional[str] = None
    title: Optional[str] = None
    area: Optional[str] = None
    note: Optional[str] = None
    code: Optional[str] = None
    station: Optional[str] = None
    shift: Optional[str] = None
    closed_at: Optional[datetime] = None
    kind: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventsResponse(BaseModel):
    items: List[EventItem]
    count: int
    api_build: str


class EventMutationResponse(BaseModel):
    ok: bool
    api_build: str
    item: EventItem


class DbPingResponse(BaseModel):
    db: str
    result: int
    api_build: str


class DebugEnvResponse(BaseModel):
    ok: bool
    api_build: str
    DATABASE_URL_present: bool
    DATABASE_URL_prefix: Optional[str] = None
    PORT: Optional[str] = None
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RAILWAY_PROJECT_NAME: Optional[str] = None
    RAILWAY_SERVICE_NAME: Optional[str] = None


class KpiStationItem(BaseModel):
    station: str
    open: int
    closed: int
    total: int


class KpiStationsResponse(BaseModel):
    ok: bool
    api_build: str
    items: List[KpiStationItem]


class HealthResponse(BaseModel):
    ok: bool
    service: str
    version: str

# === TL OVERVIEW SCHEMAS ===

class TLUrgencyItem(BaseModel):
    order_id: str
    codice: str
    cliente: Optional[str] = None
    due_date: Optional[str] = None
    priority_reason: Optional[str] = None
    stato: Optional[str] = None
    postazione: Optional[str] = None


class TLBlockedOrderItem(BaseModel):
    order_id: str
    codice: str
    motivo_blocco: str
    postazione: Optional[str] = None
    stato: Optional[str] = None
    note: Optional[str] = None


class TLCriticalStationItem(BaseModel):
    station: str
    load_level: Optional[str] = None
    active_orders: int = 0
    blocked_orders: int = 0
    note: Optional[str] = None


class TLSequenceItem(BaseModel):
    position: int
    order_id: str
    codice: str
    station: Optional[str] = None
    motivo: Optional[str] = None


class TLShiftAction(BaseModel):
    title: str
    description: str
    target_station: Optional[str] = None
    target_order_id: Optional[str] = None


class TLOverviewResponse(BaseModel):
    generated_at: datetime
    urgences: List[TLUrgencyItem] = Field(default_factory=list)
    blocked_orders: List[TLBlockedOrderItem] = Field(default_factory=list)
    critical_stations: List[TLCriticalStationItem] = Field(default_factory=list)
    suggested_sequence: List[TLSequenceItem] = Field(default_factory=list)
    shift_action: Optional[TLShiftAction] = None

