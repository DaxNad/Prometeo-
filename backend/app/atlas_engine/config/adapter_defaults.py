"""
ATLAS ENGINE — Adapter selection (proposal only).

This module documents a prospective configuration for selecting the
default solver adapter. It is NOT wired into the active runtime and
does not alter AtlasService or orchestrator behavior.

Keep PR #23 in Draft; this is a non‑runtime patch for review.
"""

from __future__ import annotations

# Current effective default used by the orchestrator
CURRENT_DEFAULT_ADAPTER: str = "ortools"

# Adapters available in this codebase
SUPPORTED_ADAPTERS: list[str] = [
    "ortools",  # default path (CP‑SAT scoring v1)
    "pyomo",    # LP scoring v1 with graceful fallback
    "noop",     # safety adapter (keeps system alive)
]

# Note: Runtime selection is NOT active yet.
# Any future enablement should be explicit and reviewed, without
# changing AtlasService public boundary or introducing env toggles
# silently. This file is for discussion only.

