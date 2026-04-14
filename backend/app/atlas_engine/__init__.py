"""ATLAS ENGINE deterministic core (scaffold).

This package freezes the deterministic architecture before solver logic.
Do not import DB or API routes here. The API will call services.atlas_service.
"""

from .contracts import (
    AtlasInput,
    AtlasPlan,
    AtlasDecision,
    AtlasExplanation,
    AtlasScenarioRequest,
)

__all__ = [
    "AtlasInput",
    "AtlasPlan",
    "AtlasDecision",
    "AtlasExplanation",
    "AtlasScenarioRequest",
]

