from __future__ import annotations

from typing import Any

from .post_rank_explainer import ExplainedMergeResult, enrich_merge_result
from .pre_rank_guard import run_pre_rank_guard
from .signal_normalizer import RawSignalBatch, normalize_raw_signals
from ..contracts import AtlasInput
from ..decision_merge_engine import solve_decision_merge


def run_agent_mod_bridge(raw_signals: RawSignalBatch) -> ExplainedMergeResult:
    normalized_signals = normalize_raw_signals(raw_signals)
    guard_result = run_pre_rank_guard(normalized_signals)

    if guard_result.hard_block is not None:
        return enrich_merge_result(
            guard_result.hard_block,
            normalized_signals=guard_result.normalized_signals,
            guard_issues=guard_result.issues,
        )

    solver_result = solve_decision_merge(guard_result.merge_input)
    return enrich_merge_result(
        solver_result,
        normalized_signals=guard_result.normalized_signals,
        guard_issues=guard_result.issues,
    )


def build_raw_signals_from_atlas_input(inp: AtlasInput) -> dict[str, dict[str, Any]]:
    highest_priority = _highest_priority(inp)
    queue_pressure = float(inp.capacities.get("station_queue_pressure") or 0.0)
    shared_pressure = bool(inp.capacities.get("shared_component_pressure"))
    open_events = [event for event in inp.events if str(event.status).upper() == "OPEN"]

    raw_signals: dict[str, dict[str, Any]] = {
        "component_availability_result": {"decision": "neutral"},
        "line_capacity_result": {"decision": "neutral"},
        "shipment_priority_result": {"decision": "neutral"},
        "bottleneck_pressure_result": {"decision": "neutral"},
        "phase_progress_result": {"decision": "neutral"},
        "operator_capacity_result": {"decision": "neutral"},
    }

    if highest_priority == "HIGH":
        raw_signals["shipment_priority_result"] = {
            "decision": "boost",
            "reason": "high customer priority detected",
        }
    elif highest_priority == "MEDIUM":
        raw_signals["shipment_priority_result"] = {
            "decision": "allow",
            "reason": "medium customer priority detected",
        }

    if queue_pressure > 0:
        raw_signals["line_capacity_result"] = {
            "decision": "warning",
            "score": min(1.0, queue_pressure),
            "reason": "station queue pressure present",
        }

    if open_events:
        raw_signals["bottleneck_pressure_result"] = {
            "decision": "defer",
            "reason": f"open operational event: {open_events[0].title}",
        }

    if shared_pressure:
        raw_signals["component_availability_result"] = {
            "decision": "defer",
            "reason": "shared component pressure present",
        }

    return raw_signals


def run_agent_mod_for_atlas_input(inp: AtlasInput) -> ExplainedMergeResult:
    return run_agent_mod_bridge(build_raw_signals_from_atlas_input(inp))


def _highest_priority(inp: AtlasInput) -> str:
    levels = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    best = ""
    best_score = 0

    for order in inp.orders:
        normalized = _normalize_priority(order.priority)
        score = levels.get(normalized, 0)
        if score > best_score:
            best = normalized
            best_score = score

    return best


def _normalize_priority(value: str | None) -> str:
    if not value:
        return ""
    normalized = str(value).strip().upper()
    if normalized in {"HIGH", "ALTA", "URGENTE"}:
        return "HIGH"
    if normalized in {"MEDIUM", "MEDIA"}:
        return "MEDIUM"
    if normalized in {"LOW", "BASSA"}:
        return "LOW"
    return normalized
