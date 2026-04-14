from __future__ import annotations

from typing import List
from pydantic import BaseModel

from .orders import DomainOrder
from .events import DomainEvent
from .stations import DomainStation
from .capacities import DomainCapacities


class Snapshot(BaseModel):
    station: DomainStation
    orders: List[DomainOrder] = []
    events: List[DomainEvent] = []
    capacities: DomainCapacities = DomainCapacities()

