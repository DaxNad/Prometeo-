from __future__ import annotations

from pydantic import BaseModel


class DomainStation(BaseModel):
    name: str

