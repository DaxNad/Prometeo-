"""PROMETEO signal classifier boundary.

This package captures lightweight intake classification before deterministic
planning and decision merge layers.
"""

from .contracts import SignalClass, SignalEnvelope

__all__ = ["SignalClass", "SignalEnvelope"]
