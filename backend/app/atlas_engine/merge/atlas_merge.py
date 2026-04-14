from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Literal, Optional, Any, Iterable, Tuple


# Decision space required by PROMETEO ATLAS ENGINE
Decision = Literal["BLOCK", "DEFER", "ALLOW", "BOOST", "INVESTIGATE"]


@dataclass(frozen=True)
class AnalyzerVote:
    """Normalized output of a single analyzer for one order.

    Keep the surface minimal and explicit. All fields are optional but
    merging logic behaves deterministically given missing fields.
    """

    module: str
    decision: Optional[Decision] = None
    # normalized priority in [0,1]; if unavailable use None
    priority: Optional[float] = None
    # optional scoring proxy (kept for future OR-Tools/Pyomo tie-breaks)
    score: Optional[float] = None
    # hard constraints raised by the analyzer (BLOCK domain)
    active_constraints: List[str] = field(default_factory=list)
    # non-blocking conflicts (soft signals)
    detected_conflicts: List[str] = field(default_factory=list)
    # concise human reasons
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MergeConfig:
    # thresholds are used only when there are no BLOCKs
    boost_priority_threshold: float = 0.8
    defer_priority_threshold: float = 0.2  # very low priority with conflicts → DEFER
    defer_if_conflicts: bool = True
    investigate_on_empty_votes: bool = True


def _norm_decision(d: Optional[str]) -> Optional[Decision]:
    if d is None:
        return None
    t = str(d).strip().upper()
    if t in {"BLOCK", "DEFER", "ALLOW", "BOOST", "INVESTIGATE"}:
        return t  # type: ignore[return-value]
    return None


def _short_explain(reasons: List[str], fallback: str) -> str:
    if reasons:
        # Take first meaningful reason; keep it short
        return reasons[0][:160]
    return fallback


def merge_order_votes(order_id: str, votes: List[AnalyzerVote], cfg: Optional[MergeConfig] = None) -> Dict[str, object]:
    """Fuse analyzer votes into a single explainable decision for an order.

    Hierarchy:
      1) Blocking constraints dominate → BLOCK
      2) Operational priorities → BOOST/ALLOW/DEFER
      3) Fine optimization (score-based tie-break) — optional and deterministic

    The merge is non-statistical and order-independent (deterministic by sorting modules).
    """
    cfg = cfg or MergeConfig()
    # defensive copy in deterministic order by module name
    votes_sorted = sorted(votes or [], key=lambda v: (v.module or "").lower())

    # 0) empty votes handling
    if not votes_sorted:
        result: Decision = "INVESTIGATE" if cfg.investigate_on_empty_votes else "ALLOW"
        return {
            "order_id": order_id,
            "merge_result": result,
            "final_priority": 0.0,
            "score": 0.0,
            "active_constraints": [],
            "detected_conflicts": [],
            "agreeing_modules": [],
            "disagreeing_modules": [],
            "main_reasons": ["nessun voto disponibile"],
            "explain_short": "nessun voto disponibile",
        }

    # 1) Blocking layer
    active_constraints: List[str] = []
    for v in votes_sorted:
        active_constraints.extend(v.active_constraints or [])
        if _norm_decision(v.decision) == "BLOCK" or (v.active_constraints and len(v.active_constraints) > 0):
            reasons = list(v.reasons or [])
            if not reasons:
                reasons = ["vincolo bloccante presente"]
            return _final(
                order_id,
                merge_result="BLOCK",
                final_priority=max(0.0, max((vv.priority or 0.0) for vv in votes_sorted)),
                score=_agg_score(votes_sorted),
                active_constraints=_dedup(active_constraints),
                detected_conflicts=_dedup(_collect(votes_sorted, "detected_conflicts")),
                votes=votes_sorted,
                reasons=reasons,
            )

    # 2) Operational priority + conflicts
    final_priority = max((v.priority or 0.0) for v in votes_sorted)
    conflicts = _dedup(_collect(votes_sorted, "detected_conflicts"))

    # Strong conflicts + very low priority → DEFER
    if cfg.defer_if_conflicts and conflicts and final_priority <= cfg.defer_priority_threshold:
        reasons = ["conflitti operativi con priorità bassa"]
        reasons.extend(conflicts[:2])
        return _final(
            order_id,
            merge_result="DEFER",
            final_priority=final_priority,
            score=_agg_score(votes_sorted),
            active_constraints=_dedup(active_constraints),
            detected_conflicts=conflicts,
            votes=votes_sorted,
            reasons=reasons,
        )

    # boost se alta priorità e nessuna controindicazione forte
    if final_priority >= cfg.boost_priority_threshold and not conflicts:
        reasons = ["priorità operativa elevata"]
        return _final(
            order_id,
            merge_result="BOOST",
            final_priority=final_priority,
            score=_agg_score(votes_sorted),
            active_constraints=_dedup(active_constraints),
            detected_conflicts=conflicts,
            votes=votes_sorted,
            reasons=reasons,
        )

    # 3) Fine optimization or neutral allow
    # If scores disagree substantially and decisions diverge, suggest INVESTIGATE
    decs = {_norm_decision(v.decision) for v in votes_sorted if v.decision is not None}
    if decs and len(decs) > 1 and conflicts:
        reasons = ["disaccordo tra moduli su decisione"]
        return _final(
            order_id,
            merge_result="INVESTIGATE",
            final_priority=final_priority,
            score=_agg_score(votes_sorted),
            active_constraints=_dedup(active_constraints),
            detected_conflicts=conflicts,
            votes=votes_sorted,
            reasons=reasons,
        )

    # otherwise ALLOW with deterministic score proxy
    return _final(
        order_id,
        merge_result="ALLOW",
        final_priority=final_priority,
        score=_agg_score(votes_sorted),
        active_constraints=_dedup(active_constraints),
        detected_conflicts=conflicts,
        votes=votes_sorted,
        reasons=["condizioni regolari"],
    )


# ---------------------- High-level signal API (v1) ----------------------

Status = Literal["OK", "WARNING", "BLOCK", "BOOST", "INFO"]


@dataclass(frozen=True)
class AnalyzerSignal:
    module_name: str
    order_id: str
    status: Status = "OK"
    priority_delta: float = 0.0  # contribution in [-1, +1]
    score: float = 0.0
    blocking_constraints: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def group_signals_by_order(signals: Iterable[AnalyzerSignal]) -> Dict[str, List[AnalyzerSignal]]:
    buckets: Dict[str, List[AnalyzerSignal]] = {}
    for s in signals or []:
        buckets.setdefault(s.order_id, []).append(s)
    # determinismo: ordina per nome modulo
    for k in list(buckets.keys()):
        buckets[k] = sorted(buckets[k], key=lambda x: x.module_name.lower())
    return buckets


def detect_blocking_constraints(signals_for_order: List[AnalyzerSignal]) -> List[str]:
    out: List[str] = []
    for s in signals_for_order:
        out.extend(s.blocking_constraints or [])
        if s.status == "BLOCK" and not s.blocking_constraints:
            out.append("BLOCK_BY_STATUS")
    return _dedup(out)


def detect_conflicts(signals_for_order: List[AnalyzerSignal]) -> List[str]:
    # conflitti soft: unione dei warnings
    out: List[str] = []
    for s in signals_for_order:
        out.extend(s.warnings or [])
    return _dedup(out)


def compute_final_priority(signals_for_order: List[AnalyzerSignal]) -> float:
    # baseline 0.5 + somma delta, clamp [0,1]
    base = 0.5
    total = base + sum(float(s.priority_delta or 0.0) for s in signals_for_order)
    return max(0.0, min(1.0, float(total)))


def _map_status_to_decision(status: Status) -> Optional[Decision]:
    m = {
        "BLOCK": "BLOCK",
        "WARNING": "DEFER",
        "BOOST": "BOOST",
        "OK": "ALLOW",
        "INFO": None,
    }
    return m.get(status)


def merge_order_signals(order_id: str, signals_for_order: List[AnalyzerSignal], cfg: Optional[MergeConfig] = None) -> Dict[str, object]:
    # traduci segnali in voti
    votes: List[AnalyzerVote] = []
    for s in signals_for_order:
        votes.append(
            AnalyzerVote(
                module=s.module_name,
                decision=_map_status_to_decision(s.status),
                priority=max(0.0, min(1.0, 0.5 + (s.priority_delta or 0.0))),
                score=float(s.score or 0.0),
                active_constraints=list(s.blocking_constraints or []),
                detected_conflicts=list(s.warnings or []),
                reasons=list(s.reasons or []),
            )
        )

    merged = merge_order_votes(order_id, votes, cfg)

    # sostituisci final_priority con quella calcolata da signals (più esplicita)
    merged = dict(merged)
    merged["final_priority"] = round(compute_final_priority(signals_for_order), 6)
    # assicurati che i vincoli/conflitti includano tutti i segnali
    merged["active_constraints"] = _dedup(list(merged.get("active_constraints", [])) + detect_blocking_constraints(signals_for_order))
    merged["detected_conflicts"] = _dedup(list(merged.get("detected_conflicts", [])) + detect_conflicts(signals_for_order))
    merged["explain_short"] = build_explain_short(merged["merge_result"], merged.get("main_reasons", []))
    return merged


def build_explain_short(merge_result: Decision, reasons: List[str]) -> str:
    if reasons:
        return reasons[0][:160]
    return f"decisione {merge_result}"


def merge_all(signals: Iterable[AnalyzerSignal], cfg: Optional[MergeConfig] = None) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for order_id, group in group_signals_by_order(signals).items():
        out.append(merge_order_signals(order_id, group, cfg))
    # determinismo finale: ordina per order_id
    out.sort(key=lambda x: str(x.get("order_id", "")))
    return out


def _final(
    order_id: str,
    *,
    merge_result: Decision,
    final_priority: float,
    score: float,
    active_constraints: List[str],
    detected_conflicts: List[str],
    votes: List[AnalyzerVote],
    reasons: List[str],
) -> Dict[str, object]:
    agree, disagree = _agreement(votes, merge_result)
    return {
        "order_id": order_id,
        "merge_result": merge_result,
        "final_priority": round(float(final_priority), 6),
        "score": round(float(score), 6),
        "active_constraints": active_constraints,
        "detected_conflicts": detected_conflicts,
        "agreeing_modules": agree,
        "disagreeing_modules": disagree,
        "main_reasons": reasons,
        "explain_short": _short_explain(reasons, f"decisione {merge_result}"),
    }


def _dedup(items: List[str]) -> List[str]:
    seen: Dict[str, bool] = {}
    out: List[str] = []
    for x in items or []:
        k = str(x)
        if k not in seen:
            seen[k] = True
            out.append(k)
    return out


def _collect(votes: List[AnalyzerVote], field_name: str) -> List[str]:
    out: List[str] = []
    for v in votes:
        val = getattr(v, field_name, None)
        if isinstance(val, list):
            out.extend([str(x) for x in val])
    return out


def _agg_score(votes: List[AnalyzerVote]) -> float:
    # deterministic average of available scores; missing treated as 0
    if not votes:
        return 0.0
    s = sum(float(v.score or 0.0) for v in votes)
    return s / float(len(votes))


def _agreement(votes: List[AnalyzerVote], final: Decision) -> (List[str], List[str]):
    agree: List[str] = []
    disagree: List[str] = []
    for v in votes:
        vd = _norm_decision(v.decision)
        if vd is None:
            continue
        if vd == final:
            agree.append(v.module)
        else:
            disagree.append(v.module)
    return (sorted(agree), sorted(disagree))
