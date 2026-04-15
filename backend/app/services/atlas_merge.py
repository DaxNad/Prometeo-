from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BLOCKING_OUTCOMES = {"BLOCK", "HARD_BLOCK"}
POSITIVE_OUTCOMES = {"PROCEED", "ACCELERATE"}
NEGATIVE_OUTCOMES = {"REVIEW", "DEFER", "HOLD"}


@dataclass(frozen=True)
class MergeSignal:
    module: str
    outcome: str
    score: float
    reasons: list[str]
    active_constraints: list[str]


def _norm_outcome(raw: Any) -> str:
    value = str(raw or "").strip().upper()
    if value in BLOCKING_OUTCOMES | POSITIVE_OUTCOMES | NEGATIVE_OUTCOMES:
        return value
    return "MONITOR"


def _norm_score(raw: Any) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, value))


def _norm_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        values = raw
    else:
        values = [raw]

    normalized: list[str] = []
    for item in values:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _normalize_signal(raw: dict[str, Any]) -> MergeSignal:
    return MergeSignal(
        module=str(raw.get("module", "unknown")).strip() or "unknown",
        outcome=_norm_outcome(raw.get("outcome")),
        score=_norm_score(raw.get("score")),
        reasons=_norm_list(raw.get("reasons")),
        active_constraints=_norm_list(raw.get("active_constraints")),
    )


def merge_atlas_v1(signals: list[dict[str, Any]] | None) -> dict[str, Any]:
    normalized = [_normalize_signal(signal) for signal in (signals or [])]

    if not normalized:
        return {
            "final_outcome": "MONITOR",
            "final_score": 0.0,
            "reasons": ["no strong deterministic signals available"],
            "active_constraints": [],
            "conflicts": [],
            "consensus": {
                "modules_considered": 0,
                "agreement_ratio": 0.0,
                "outcome_votes": {},
            },
            "explain_brief": "Fallback MONITOR: nessun segnale forte disponibile.",
        }

    outcome_votes: dict[str, int] = {}
    reasons: list[str] = []
    constraints: list[str] = []

    for signal in sorted(normalized, key=lambda x: x.module):
        outcome_votes[signal.outcome] = outcome_votes.get(signal.outcome, 0) + 1
        reasons.extend(signal.reasons)
        constraints.extend(signal.active_constraints)

    reasons = sorted({reason for reason in reasons})
    active_constraints = sorted({constraint for constraint in constraints})

    has_blocking_constraint = any(c.upper().startswith("BLOCK") for c in active_constraints)
    has_blocking_outcome = any(signal.outcome in BLOCKING_OUTCOMES for signal in normalized)

    positive_votes = sum(1 for signal in normalized if signal.outcome in POSITIVE_OUTCOMES)
    negative_votes = sum(1 for signal in normalized if signal.outcome in NEGATIVE_OUTCOMES)

    final_score = round(sum(signal.score for signal in normalized) / len(normalized), 4)

    if has_blocking_constraint or has_blocking_outcome:
        final_outcome = "BLOCK"
    elif positive_votes > negative_votes and final_score >= 0.55:
        final_outcome = "PROCEED"
    elif negative_votes > positive_votes:
        final_outcome = "REVIEW"
    else:
        final_outcome = "MONITOR"

    conflicts: list[str] = []
    distinct_outcomes = sorted({signal.outcome for signal in normalized})
    if len(distinct_outcomes) > 1:
        for signal in sorted(normalized, key=lambda x: x.module):
            conflicts.append(f"{signal.module}:{signal.outcome}")

    for signal in sorted(normalized, key=lambda x: x.module):
        if final_outcome == "BLOCK" and signal.outcome not in BLOCKING_OUTCOMES:
            conflicts.append(f"{signal.module}:{signal.outcome}->BLOCK")
        elif final_outcome == "PROCEED" and signal.outcome in NEGATIVE_OUTCOMES | BLOCKING_OUTCOMES:
            conflicts.append(f"{signal.module}:{signal.outcome}->PROCEED")
        elif final_outcome == "REVIEW" and signal.outcome in POSITIVE_OUTCOMES:
            conflicts.append(f"{signal.module}:{signal.outcome}->REVIEW")

    winning_votes = outcome_votes.get(final_outcome, 0)
    agreement_ratio = round(winning_votes / len(normalized), 4)

    explain_brief = (
        f"ATLAS merge v1 => {final_outcome} "
        f"(score={final_score:.2f}, moduli={len(normalized)}, conflitti={len(conflicts)})."
    )

    return {
        "final_outcome": final_outcome,
        "final_score": final_score,
        "reasons": reasons,
        "active_constraints": active_constraints,
        "conflicts": conflicts,
        "consensus": {
            "modules_considered": len(normalized),
            "agreement_ratio": agreement_ratio,
            "outcome_votes": dict(sorted(outcome_votes.items(), key=lambda x: x[0])),
        },
        "explain_brief": explain_brief,
    }


def build_sequence_signals(item: dict[str, Any]) -> list[dict[str, Any]]:
    priority = str(item.get("customer_priority", "")).strip().upper()
    open_events_total = int(item.get("open_events_total", 0) or 0)
    station_rank = int(item.get("station_rank", 0) or 0)

    priority_signal = {
        "module": "priority_module",
        "outcome": "PROCEED" if priority in {"CRITICA", "ALTA"} else "MONITOR",
        "score": 0.8 if priority in {"CRITICA", "ALTA"} else 0.4,
        "reasons": [f"customer_priority={priority or 'ND'}"],
        "active_constraints": [],
    }

    event_signal = {
        "module": "event_guard_module",
        "outcome": "BLOCK" if open_events_total > 0 else "PROCEED",
        "score": 0.9 if open_events_total > 0 else 0.7,
        "reasons": [f"open_events_total={open_events_total}"],
        "active_constraints": ["BLOCKING_OPEN_EVENTS"] if open_events_total > 0 else [],
    }

    queue_signal = {
        "module": "queue_pressure_module",
        "outcome": "REVIEW" if station_rank >= 8 else "PROCEED",
        "score": 0.65 if station_rank >= 8 else 0.6,
        "reasons": [f"station_rank={station_rank}"],
        "active_constraints": [],
    }

    return [priority_signal, event_signal, queue_signal]
