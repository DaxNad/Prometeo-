"""Minimal ATLAS agent_mod shell around the pure decision merge solver."""

from .agent_mod_bridge import (
    build_raw_signals_from_atlas_input,
    run_agent_mod_bridge,
    run_agent_mod_for_atlas_input,
)

__all__ = [
    "build_raw_signals_from_atlas_input",
    "run_agent_mod_bridge",
    "run_agent_mod_for_atlas_input",
]
