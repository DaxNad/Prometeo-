from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, Any


class DomainCapacities(BaseModel):
    values: Dict[str, Any] = {}

