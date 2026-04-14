from __future__ import annotations

from .normalization import normalize_station
from ..contracts import AtlasInput
from ..domain.snapshot import Snapshot
from ..domain.orders import DomainOrder
from ..domain.events import DomainEvent
from ..domain.stations import DomainStation
from ..domain.capacities import DomainCapacities


def build_snapshot(inp: AtlasInput) -> Snapshot:
    station = DomainStation(name=normalize_station(inp.station))
    orders = [
        DomainOrder(
            order_id=o.order_id,
            code=o.code,
            quantity=o.quantity,
            station=normalize_station(o.station),
            priority=o.priority,
            status=o.status,
        )
        for o in inp.orders
    ]
    events = [
        DomainEvent(
            station=normalize_station(e.station) or "",
            title=e.title,
            status=e.status,
            event_type=e.event_type,
            severity=e.severity,
        )
        for e in inp.events
    ]
    capacities = DomainCapacities(values=dict(inp.capacities or {}))
    return Snapshot(station=station, orders=orders, events=events, capacities=capacities)

