"""
ATLAS ENGINE — PenaltyConfig calibration (proposal only).

This module freezes proposed defaults and safe ranges so they can be
reviewed and eventually enabled later, without changing current behavior.

Do NOT import these values into the active solve path yet.
"""

from __future__ import annotations

from typing import Dict, Tuple


# Parameters covered
PARAMETERS = (
    "blocked_penalty",
    "shared_component_penalty",
    "open_event_penalty",
    "station_pressure_penalty",
    "assembly_coherence_penalty",
    "max_blocked_in_top_k",
    "top_k_window",
    "blocked_excess_penalty",
)


# Current runtime defaults (as implemented in ORToolsAdapter.PenaltyConfig)
CURRENT_DEFAULTS: Dict[str, float | int] = {
    "blocked_penalty": 100.0,
    "shared_component_penalty": 1.0,
    "open_event_penalty": 1.0,
    "station_pressure_penalty": 0.10,
    "assembly_coherence_penalty": 0.01,
    "max_blocked_in_top_k": 1,
    "top_k_window": 3,
    "blocked_excess_penalty": 5.0,
}


# Proposed calibration (do NOT wire to runtime yet)
PROPOSED_DEFAULTS: Dict[str, float | int] = {
    "blocked_penalty": 100.0,
    "shared_component_penalty": 1.0,
    "open_event_penalty": 1.0,
    "station_pressure_penalty": 0.10,
    "assembly_coherence_penalty": 0.01,
    "max_blocked_in_top_k": 1,
    "top_k_window": 3,
    "blocked_excess_penalty": 5.0,
}


# Recommended safe ranges (inclusive), expressed as (min, max)
SAFE_RANGES: Dict[str, Tuple[float | int, float | int]] = {
    "blocked_penalty": (80.0, 120.0),
    "shared_component_penalty": (0.5, 2.0),
    "open_event_penalty": (0.5, 2.0),
    "station_pressure_penalty": (0.05, 0.15),
    "assembly_coherence_penalty": (0.005, 0.02),
    "max_blocked_in_top_k": (1, 2),
    "top_k_window": (3, 5),
    "blocked_excess_penalty": (3.0, 8.0),
}


def _all_keys_ok() -> bool:
    return set(PARAMETERS) <= set(CURRENT_DEFAULTS) == set(PROPOSED_DEFAULTS) == set(SAFE_RANGES)

