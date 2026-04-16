"""PROMETEO decision merge boundary.

This package defines how deterministic planner outputs can be enriched by
soft advisory signals without changing sequencing authority.
"""

from .contracts import AdvisorySource, MergeDecision

__all__ = ["AdvisorySource", "MergeDecision"]
