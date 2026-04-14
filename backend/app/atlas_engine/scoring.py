from __future__ import annotations

from typing import List

from .contracts import AtlasOrder
from .constants import PRIORITY_WEIGHTS


def stable_score(orders: List[AtlasOrder]) -> List[AtlasOrder]:
    def key(o: AtlasOrder):
        w = PRIORITY_WEIGHTS.get((o.priority or "").upper(), 0)
        blocked = 1 if (o.status or "").lower() == "bloccato" else 0
        # sort: blocked first (desc), then weight desc, then order_id for stability
        return (-blocked, -w, o.order_id)

    return sorted(orders, key=key)

