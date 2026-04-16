from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SignalClass = Literal["normal", "anomaly", "warning"]


@dataclass(frozen=True)
class SignalEnvelope:
    """Intake-layer signal contract used by runtime/bridge components."""

    source: str
    station: str
    severity: str
    signal_class: SignalClass
