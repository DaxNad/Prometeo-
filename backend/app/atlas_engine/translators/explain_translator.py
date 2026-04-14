from __future__ import annotations

from typing import Dict, Any
from ..contracts import AtlasExplanation


def to_explain_payload(expl: AtlasExplanation) -> Dict[str, Any]:
    return expl.model_dump()

