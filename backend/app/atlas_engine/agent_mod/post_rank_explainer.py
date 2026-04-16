from __future__ import annotations

from dataclasses import dataclass, field

from ..decision_merge_engine import FinalDecision, MergeResult, MergeSignal


@dataclass
class ExplainedMergeResult:
    decision: FinalDecision
    priority_score: float
    active_constraints: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    explain: str = ""
    explain_short: str = ""
    main_reasons: list[str] = field(default_factory=list)
    agreeing_modules: list[str] = field(default_factory=list)
    disagreeing_modules: list[str] = field(default_factory=list)
    guard_issues: list[str] = field(default_factory=list)


def enrich_merge_result(
    result: MergeResult,
    normalized_signals: list[MergeSignal],
    guard_issues: list[str] | None = None,
) -> ExplainedMergeResult:
    issues = list(guard_issues or [])
    main_reasons = _build_main_reasons(result, normalized_signals, issues)
    agreeing_modules, disagreeing_modules = _classify_modules(
        decision=result.decision,
        normalized_signals=normalized_signals,
    )
    explain_short = f"{result.decision}: {main_reasons[0]}" if main_reasons else result.explain
    explain = result.explain
    if issues:
        explain = f"{explain} Guard issues: {', '.join(issues[:2])}."

    return ExplainedMergeResult(
        decision=result.decision,
        priority_score=result.priority_score,
        active_constraints=list(result.active_constraints),
        conflicts=list(result.conflicts),
        explain=explain,
        explain_short=explain_short,
        main_reasons=main_reasons,
        agreeing_modules=agreeing_modules,
        disagreeing_modules=disagreeing_modules,
        guard_issues=issues,
    )


def _build_main_reasons(
    result: MergeResult,
    normalized_signals: list[MergeSignal],
    guard_issues: list[str],
) -> list[str]:
    reasons = _dedupe(
        list(result.active_constraints)
        + list(result.conflicts)
        + guard_issues
        + [reason for signal in normalized_signals for reason in signal.reasons]
    )
    if reasons:
        return reasons[:3]
    return [result.explain]


def _classify_modules(
    *,
    decision: FinalDecision,
    normalized_signals: list[MergeSignal],
) -> tuple[list[str], list[str]]:
    agreeing: list[str] = []
    disagreeing: list[str] = []
    seen_agreeing: set[str] = set()
    seen_disagreeing: set[str] = set()

    for signal in normalized_signals:
        if signal.decision == "NEUTRAL" or not signal.source_module:
            continue
        if _supports_final_decision(signal.decision, decision):
            if signal.source_module not in seen_agreeing:
                seen_agreeing.add(signal.source_module)
                agreeing.append(signal.source_module)
        else:
            if signal.source_module not in seen_disagreeing:
                seen_disagreeing.add(signal.source_module)
                disagreeing.append(signal.source_module)

    return agreeing, disagreeing


def _supports_final_decision(signal_decision: str, final_decision: FinalDecision) -> bool:
    if final_decision == "BOOST":
        return signal_decision in {"BOOST", "ALLOW"}
    return signal_decision == final_decision


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
