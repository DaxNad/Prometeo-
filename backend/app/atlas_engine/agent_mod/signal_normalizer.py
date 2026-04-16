from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..decision_merge_engine import MergeSignal, SignalDecision


RawSignal = MergeSignal | Mapping[str, Any]
RawSignalBatch = Mapping[str, RawSignal] | Sequence[RawSignal]

_CANONICAL_SOURCES: tuple[str, ...] = (
    "component_availability",
    "line_capacity",
    "shipment_priority",
    "bottleneck_pressure",
    "phase_progress",
    "operator_capacity",
)
_SOURCE_TO_FIELD: dict[str, str] = {
    "component_availability": "component_availability_result",
    "line_capacity": "line_capacity_result",
    "shipment_priority": "shipment_priority_result",
    "bottleneck_pressure": "bottleneck_pressure_result",
    "phase_progress": "phase_progress_result",
    "operator_capacity": "operator_capacity_result",
}
_SOURCE_ALIASES: dict[str, str] = {
    "component_availability": "component_availability",
    "component_availability_result": "component_availability",
    "line_capacity": "line_capacity",
    "line_capacity_result": "line_capacity",
    "shipment_priority": "shipment_priority",
    "shipment_priority_result": "shipment_priority",
    "bottleneck_pressure": "bottleneck_pressure",
    "bottleneck_pressure_result": "bottleneck_pressure",
    "phase_progress": "phase_progress",
    "phase_progress_result": "phase_progress",
    "operator_capacity": "operator_capacity",
    "operator_capacity_result": "operator_capacity",
}
_DECISION_ALIASES: dict[str, SignalDecision] = {
    "ALLOW": "ALLOW",
    "BLOCK": "BLOCK",
    "DEFER": "DEFER",
    "BOOST": "BOOST",
    "NEUTRAL": "NEUTRAL",
    "OK": "ALLOW",
    "WARNING": "DEFER",
    "INFO": "NEUTRAL",
}


def normalize_raw_signals(raw_signals: RawSignalBatch) -> list[MergeSignal]:
    normalized: list[MergeSignal] = []
    for hinted_source, raw_signal in _iter_raw_signals(raw_signals):
        signal = _normalize_single_signal(raw_signal, hinted_source=hinted_source)
        if signal is not None:
            normalized.append(signal)
    return normalized


def canonical_sources() -> tuple[str, ...]:
    return _CANONICAL_SOURCES


def merge_input_field_for_source(source_module: str) -> str | None:
    canonical = _canonical_source(source_module)
    if canonical is None:
        return None
    return _SOURCE_TO_FIELD[canonical]


def _iter_raw_signals(
    raw_signals: RawSignalBatch,
) -> list[tuple[str | None, RawSignal]]:
    if isinstance(raw_signals, Mapping):
        return [(str(key), value) for key, value in raw_signals.items()]
    return [(None, value) for value in raw_signals]


def _normalize_single_signal(
    raw_signal: RawSignal,
    *,
    hinted_source: str | None,
) -> MergeSignal | None:
    if isinstance(raw_signal, MergeSignal):
        source_module = _canonical_source(raw_signal.source_module or hinted_source)
        if source_module is None:
            return None
        return MergeSignal(
            decision=_normalize_decision(raw_signal.decision),
            score=_normalize_optional_float(raw_signal.score),
            confidence=_normalize_optional_float(raw_signal.confidence),
            reasons=_normalize_reasons(raw_signal.reasons),
            source_module=source_module,
        )

    source_module = _canonical_source(
        raw_signal.get("source_module")
        or raw_signal.get("module")
        or raw_signal.get("name")
        or hinted_source
    )
    if source_module is None:
        return None

    return MergeSignal(
        decision=_normalize_decision(raw_signal.get("decision") or raw_signal.get("status")),
        score=_normalize_optional_float(raw_signal.get("score")),
        confidence=_normalize_optional_float(raw_signal.get("confidence")),
        reasons=_normalize_reasons(raw_signal.get("reasons") or raw_signal.get("reason")),
        source_module=source_module,
    )


def _canonical_source(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    return _SOURCE_ALIASES.get(normalized)


def _normalize_decision(value: Any) -> SignalDecision:
    if value is None:
        return "NEUTRAL"
    normalized = str(value).strip().upper()
    return _DECISION_ALIASES.get(normalized, "NEUTRAL")


def _normalize_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return _clamp(float(value))


def _normalize_reasons(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if str(item).strip()]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
