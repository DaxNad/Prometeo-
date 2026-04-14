from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AtlasOrder(BaseModel):
    order_id: str
    code: Optional[str] = None
    quantity: Optional[int] = 0
    station: Optional[str] = None
    priority: Optional[str] = None  # e.g., ALTA, MEDIA, BASSA
    status: Optional[str] = None  # e.g., OPEN/BLOCKED/etc (domain-specific)


class AtlasEvent(BaseModel):
    station: str
    title: str
    status: str = "OPEN"  # OPEN/CLOSED
    event_type: Optional[str] = None  # QUEUE/BLOCK/MATERIAL_DELAY
    severity: Optional[str] = None


class AtlasInput(BaseModel):
    station: str
    orders: List[AtlasOrder] = Field(default_factory=list)
    events: List[AtlasEvent] = Field(default_factory=list)
    capacities: Dict[str, Any] = Field(default_factory=dict)


class AtlasDecision(BaseModel):
    sequence: List[str] = Field(default_factory=list)  # list of order_id
    adapter: str = "fallback"


class AtlasPlan(BaseModel):
    sequence: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class AtlasExplanation(BaseModel):
    reasons: List[str] = Field(default_factory=list)
    risk_level: str = "LOW"
    signals: Dict[str, Any] = Field(default_factory=dict)


class AtlasScenarioRequest(BaseModel):
    station: str
    orders: List[AtlasOrder] = Field(default_factory=list)
    events: List[AtlasEvent] = Field(default_factory=list)
    capacities: Dict[str, Any] = Field(default_factory=dict)

