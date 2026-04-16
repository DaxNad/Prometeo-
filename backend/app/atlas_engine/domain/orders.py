from __future__ import annotations

from pydantic import BaseModel


class DomainOrder(BaseModel):
    order_id: str
    code: str | None = None
    quantity: int | None = 0
    station: str | None = None
    priority: str | None = None
    status: str | None = None

