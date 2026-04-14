from __future__ import annotations

from typing import List

from .contracts import AtlasInput
from .scoring import stable_score


def generate(inp: AtlasInput) -> List[str]:
    # produce a deterministic sequence using simple stable scoring
    scored = stable_score(inp.orders)
    return [o.order_id for o in scored]

