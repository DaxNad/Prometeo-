from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentAnalyzeRequest(BaseModel):
    source: str = Field(..., description="Origine evento o chiamata runtime")
    line_id: str = Field(..., description="Linea o contesto operativo")
    event_type: str = Field(..., description="Tipo evento")
    severity: str = Field(default="info", description="Livello severità")
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentDecision(BaseModel):
    decision_mode: str
    action: str
    explanation: str


class AgentAnalyzeResponse(BaseModel):
    inspection: dict[str, Any]
    decision: AgentDecision


class AgentRunRecord(BaseModel):
    id: int
    source: str
    line_id: str
    event_type: str
    severity: str | None
    inspection_json: dict[str, Any]
    decision_mode: str
    action: str
    explanation: str | None
    created_at: datetime
