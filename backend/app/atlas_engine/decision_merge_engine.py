from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


SignalDecision = Literal["ALLOW", "BLOCK", "DEFER", "BOOST", "NEUTRAL"]
FinalDecision = Literal["BLOCK", "DEFER", "ALLOW", "BOOST"]

_DEFAULT_SIGNAL_SCORE: dict[SignalDecision, float] = {
    "BLOCK": 0.0,
    "DEFER": 0.35,
    "ALLOW": 0.60,
    "BOOST": 0.75,
    "NEUTRAL": 0.50,
}
_BOOST_BONUS = 0.15
_DEFER_CAP = 0.49
_ALLOW_FLOOR = 0.50
_BOOST_FLOOR = 0.70

_INPUT_FIELDS = (
    ("component_availability_result", "component_availability"),
    ("line_capacity_result", "line_capacity"),
    ("shipment_priority_result", "shipment_priority"),
    ("bottleneck_pressure_result", "bottleneck_pressure"),
    ("phase_progress_result", "phase_progress"),
    ("operator_capacity_result", "operator_capacity"),
)


@dataclass
class MergeSignal:
    decision: SignalDecision
    score: float | None = None
    confidence: float | None = None
    reasons: list[str] = field(default_factory=list)
    source_module: str | None = None


@dataclass
class MergeInput:
    component_availability_result: MergeSignal | None = None
    line_capacity_result: MergeSignal | None = None
    shipment_priority_result: MergeSignal | None = None
    bottleneck_pressure_result: MergeSignal | None = None
    phase_progress_result: MergeSignal | None = None
    operator_capacity_result: MergeSignal | None = None


@dataclass
class MergeResult:
    decision: FinalDecision
    priority_score: float
    active_constraints: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    explain: str = ""


def solve_decision_merge(input: MergeInput) -> MergeResult:
    """Merge heterogeneous ATLAS signals with explicit constraint precedence."""
    signals = _collect_signals(input)
    blockers = [signal for signal in signals if signal.decision == "BLOCK"]
    deferrals = [signal for signal in signals if signal.decision == "DEFER"]
    boosts = [signal for signal in signals if signal.decision == "BOOST"]
    allows = [signal for signal in signals if signal.decision == "ALLOW"]

    conflicts = _detect_conflicts(
        restrictive=blockers + deferrals,
        supportive=boosts + allows,
    )

    if blockers:
        active_constraints = _build_constraints(blockers)
        return MergeResult(
            decision="BLOCK",
            priority_score=0.0,
            active_constraints=active_constraints,
            conflicts=conflicts,
            explain=_build_explain(
                decision="BLOCK",
                active_constraints=active_constraints,
                conflicts=conflicts,
            ),
        )

    if deferrals:
        active_constraints = _build_constraints(deferrals)
        priority_score = _compute_defer_score(deferrals=deferrals, supportive=boosts + allows)
        return MergeResult(
            decision="DEFER",
            priority_score=priority_score,
            active_constraints=active_constraints,
            conflicts=conflicts,
            explain=_build_explain(
                decision="DEFER",
                active_constraints=active_constraints,
                conflicts=conflicts,
            ),
        )

    if boosts:
        active_constraints = _build_constraints(boosts)
        priority_score = _compute_positive_score(boosts, floor=_BOOST_FLOOR, add_bonus=True)
        return MergeResult(
            decision="BOOST",
            priority_score=priority_score,
            active_constraints=active_constraints,
            conflicts=conflicts,
            explain=_build_explain(
                decision="BOOST",
                active_constraints=active_constraints,
                conflicts=conflicts,
            ),
        )

    if allows:
        active_constraints = _build_constraints(allows)
        priority_score = _compute_positive_score(allows, floor=_ALLOW_FLOOR, add_bonus=False)
        return MergeResult(
            decision="ALLOW",
            priority_score=priority_score,
            active_constraints=active_constraints,
            conflicts=conflicts,
            explain=_build_explain(
                decision="ALLOW",
                active_constraints=active_constraints,
                conflicts=conflicts,
            ),
        )

    return MergeResult(
        decision="ALLOW",
        priority_score=_ALLOW_FLOOR,
        active_constraints=[],
        conflicts=[],
        explain="ALLOW because no active non-neutral constraints were produced.",
    )


@dataclass(frozen=True)
class _ResolvedSignal:
    source_module: str
    decision: SignalDecision
    score: float
    confidence: float
    reasons: tuple[str, ...]


def _collect_signals(input: MergeInput) -> list[_ResolvedSignal]:
    resolved: list[_ResolvedSignal] = []
    for field_name, default_source in _INPUT_FIELDS:
        signal = getattr(input, field_name)
        if signal is None or signal.decision == "NEUTRAL":
            continue
        resolved.append(
            _ResolvedSignal(
                source_module=signal.source_module or default_source,
                decision=signal.decision,
                score=_normalize_score(signal.score, signal.decision),
                confidence=_normalize_confidence(signal.confidence),
                reasons=tuple(signal.reasons),
            )
        )
    return resolved


def _normalize_score(score: float | None, decision: SignalDecision) -> float:
    base = _DEFAULT_SIGNAL_SCORE[decision] if score is None else score
    return _clamp(base)


def _normalize_confidence(confidence: float | None) -> float:
    if confidence is None:
        return 1.0
    return _clamp(confidence)


def _build_constraints(signals: list[_ResolvedSignal]) -> list[str]:
    constraints: list[str] = []
    for signal in signals:
        if signal.reasons:
            for reason in signal.reasons:
                constraints.append(f"{signal.source_module}: {reason}")
        else:
            constraints.append(f"{signal.source_module}: {signal.decision}")
    return _dedupe(constraints)


def _detect_conflicts(
    restrictive: list[_ResolvedSignal],
    supportive: list[_ResolvedSignal],
) -> list[str]:
    conflicts: list[str] = []
    for restrictive_signal in restrictive:
        for supportive_signal in supportive:
            conflicts.append(
                f"{restrictive_signal.source_module}:{restrictive_signal.decision}"
                f" conflicts with "
                f"{supportive_signal.source_module}:{supportive_signal.decision}"
            )
    return _dedupe(conflicts)


def _compute_defer_score(
    deferrals: list[_ResolvedSignal],
    supportive: list[_ResolvedSignal],
) -> float:
    if supportive:
        strongest_support = max(_signal_strength(signal) for signal in supportive)
    else:
        strongest_support = _DEFAULT_SIGNAL_SCORE["DEFER"]
    penalized = strongest_support * 0.5
    strongest_deferral = max(_signal_strength(signal) for signal in deferrals)
    score = min(penalized, strongest_deferral, _DEFER_CAP)
    return round(_clamp(score), 6)


def _compute_positive_score(
    signals: list[_ResolvedSignal],
    *,
    floor: float,
    add_bonus: bool,
) -> float:
    strongest_signal = max(_signal_strength(signal) for signal in signals)
    if add_bonus:
        strongest_signal += _BOOST_BONUS
    return round(_clamp(max(floor, strongest_signal)), 6)


def _signal_strength(signal: _ResolvedSignal) -> float:
    return _clamp(signal.score * signal.confidence)


def _build_explain(
    *,
    decision: FinalDecision,
    active_constraints: list[str],
    conflicts: list[str],
) -> str:
    parts = [f"{decision} by explicit constraint precedence"]
    if active_constraints:
        parts.append(f"active constraints: {', '.join(active_constraints[:3])}")
    if conflicts:
        parts.append(f"conflicts: {', '.join(conflicts[:2])}")
    return "; ".join(parts) + "."


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

