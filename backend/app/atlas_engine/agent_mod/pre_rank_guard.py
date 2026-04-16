from __future__ import annotations

from dataclasses import dataclass, field

from ..decision_merge_engine import MergeInput, MergeResult, MergeSignal
from .signal_normalizer import canonical_sources, merge_input_field_for_source


@dataclass
class PreRankGuardResult:
    merge_input: MergeInput
    normalized_signals: list[MergeSignal] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    hard_block: MergeResult | None = None


def run_pre_rank_guard(normalized_signals: list[MergeSignal]) -> PreRankGuardResult:
    grouped: dict[str, list[MergeSignal]] = {}
    for signal in normalized_signals:
        if not signal.source_module:
            continue
        grouped.setdefault(signal.source_module, []).append(signal)

    if not grouped:
        return PreRankGuardResult(
            merge_input=MergeInput(),
            normalized_signals=[],
            issues=["missing all normalized signals"],
            hard_block=_hard_block("missing all normalized signals"),
        )

    issues: list[str] = []
    merge_input = MergeInput()
    unique_signals: list[MergeSignal] = []

    for source_module in canonical_sources():
        signals = grouped.get(source_module, [])
        if not signals:
            issues.append(f"missing signal: {source_module}")
            continue

        decisions = {signal.decision for signal in signals}
        if len(decisions) > 1:
            return PreRankGuardResult(
                merge_input=MergeInput(),
                normalized_signals=signals,
                issues=[f"incoherent signal set: {source_module}"],
                hard_block=_hard_block(f"incoherent signal set: {source_module}"),
            )

        if len(signals) > 1:
            issues.append(f"duplicate signal: {source_module}")

        primary_signal = signals[0]
        unique_signals.append(primary_signal)
        field_name = merge_input_field_for_source(source_module)
        if field_name is not None:
            setattr(merge_input, field_name, primary_signal)

    return PreRankGuardResult(
        merge_input=merge_input,
        normalized_signals=unique_signals,
        issues=issues,
        hard_block=None,
    )


def _hard_block(reason: str) -> MergeResult:
    constraint = f"pre_rank_guard: {reason}"
    return MergeResult(
        decision="BLOCK",
        priority_score=0.0,
        active_constraints=[constraint],
        conflicts=[],
        explain=f"BLOCK by pre-rank guard: {reason}.",
    )
