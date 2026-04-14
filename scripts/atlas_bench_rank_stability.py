#!/usr/bin/env python3
"""
Atlas Bench — Ranking Stability (local only)

Measures sensitivity of deterministic ranking to small PenaltyConfig variations.

Scope:
- backend only, no DB, no API changes, no CI integration
- prints a compact textual report for PR discussion
"""

from __future__ import annotations

import os
import sys
import argparse
from dataclasses import replace
from typing import Dict, List, Tuple

# Make runnable from repo root without manual PYTHONPATH
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from backend.app.atlas_engine.adapters.ortools_adapter import ORToolsAdapter, PenaltyConfig
from backend.app.atlas_engine.adapters.pyomo_adapter import PyomoAdapter
from backend.app.atlas_engine.builders.constraint_builder import build_constraints
from backend.app.atlas_engine.builders.objective_builder import build_objective
from backend.app.atlas_engine.builders.snapshot_builder import build_snapshot
from backend.app.atlas_engine.contracts import AtlasEvent, AtlasOrder, AtlasScenarioRequest


def hamming_at_k(a: List[str], b: List[str], k: int) -> int:
    n = min(k, len(a), len(b))
    return sum(1 for i in range(n) if a[i] != b[i])


def swap_count(a: List[str], b: List[str]) -> int:
    # Kendall-like pair inversions among common ids
    pos_b = {oid: i for i, oid in enumerate(b)}
    ids = [x for x in a if x in pos_b]
    inv = 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            inv += int(pos_b[ids[i]] > pos_b[ids[j]])
    return inv


def totals_map(meta: Dict) -> Dict[str, float]:
    scores = meta.get("scores") or []
    out: Dict[str, float] = {}
    for s in scores:
        try:
            out[str(s.get("order_id"))] = float(s.get("total", 0))
        except Exception:
            pass
    return out


def margins_top(meta: Dict, seq: List[str], k: int = 3) -> Tuple[float, float]:
    tm = totals_map(meta)
    # margin_top1: diff between top1 and runner-up
    m1 = 0.0
    if len(seq) >= 2:
        m1 = float(tm.get(seq[0], 0.0) - tm.get(seq[1], 0.0))
    # margin_top3_min: minimum abs diff among adjacent pairs in top3
    m3 = 0.0
    n = min(3, len(seq))
    if n >= 2:
        diffs = [abs(float(tm.get(seq[i], 0.0) - tm.get(seq[i + 1], 0.0))) for i in range(n - 1)]
        m3 = min(diffs) if diffs else 0.0
    return m1, m3


def near_flip_risk(meta: Dict, seq: List[str], k: int = 3, eps: float = 0.5) -> int:
    tm = totals_map(meta)
    n = min(k, len(seq))
    risk = 0
    for i in range(n - 1):
        if abs(float(tm.get(seq[i], 0.0) - tm.get(seq[i + 1], 0.0))) < eps:
            risk += 1
    return risk


def blocked_topk_violations(seq: List[str], feasible_map: Dict[str, bool], cfg: PenaltyConfig) -> int:
    if cfg.top_k_window <= 0:
        return 0
    top = seq[: cfg.top_k_window]
    blocked = sum(1 for oid in top if not feasible_map.get(oid, True))
    return max(0, blocked - cfg.max_blocked_in_top_k)


def assembly_incoherence(seq: List[str], code_map: Dict[str, str]) -> int:
    # Count groups where the order_ids are not lexicographically sorted in the sequence
    groups: Dict[str, List[str]] = {}
    for oid in seq:
        g = code_map.get(oid)
        if g:
            groups.setdefault(g, []).append(oid)
    incoh = 0
    for g, oids in groups.items():
        if len(oids) < 2:
            continue
        if oids != sorted(oids):
            incoh += 1
    return incoh


def solve_req(req: AtlasScenarioRequest, cfg: PenaltyConfig | None = None, adapter: str = "ortools") -> Tuple[List[str], Dict]:
    snap = build_snapshot(req)
    cons = build_constraints(snap)
    obj = build_objective(snap)
    if adapter == "pyomo":
        res = PyomoAdapter(config=cfg).solve(snap, cons, obj)
    else:
        res = ORToolsAdapter(config=cfg).solve(snap, cons, obj)
    return list(res.get("sequence", [])), dict(res.get("meta", {}))


def make_probes() -> List[Tuple[str, AtlasScenarioRequest]]:
    base = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="P1", station="ZAW-1", priority="ALTA", quantity=5),
            AtlasOrder(order_id="P2", station="ZAW-1", priority="MEDIA", quantity=3),
            AtlasOrder(order_id="P3", station="ZAW-1", priority="BASSA", quantity=2),
        ],
    )
    blocked = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="B1", station="ZAW-1", priority="ALTA", status="bloccato", quantity=2),
            AtlasOrder(order_id="B2", station="ZAW-1", priority="MEDIA", status="bloccato", quantity=2),
            AtlasOrder(order_id="F1", station="ZAW-1", priority="MEDIA", quantity=2),
        ],
    )
    shared = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="S10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="S01", station="ZAW-1", priority="MEDIA", quantity=1),
        ],
        capacities={"shared_component_pressure": True, "station_queue_pressure": 2},
    )
    group = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="G02", station="ZAW-1", priority="MEDIA", code="AG-1", quantity=5),
            AtlasOrder(order_id="G01", station="ZAW-1", priority="MEDIA", code="AG-1", quantity=5),
        ],
    )
    open_evt = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="E2", station="ZAW-1", priority="MEDIA", quantity=3),
            AtlasOrder(order_id="E1", station="ZAW-1", priority="MEDIA", quantity=3),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
    )
    # Near-tie: priority vs (global) event — event is uniform, use quantity to create near-tie vs priority
    near_tie_priority_event = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="NT_PE_HI", station="ZAW-1", priority="ALTA", quantity=12),
            AtlasOrder(order_id="NT_PE_MD", station="ZAW-1", priority="MEDIA", quantity=10),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
        capacities={"station_queue_pressure": 52},
    )
    # Near-tie: shared vs station pressure — small quantity gap under shared_component_pressure
    near_tie_shared_station = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="NT_SS_10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="NT_SS_09", station="ZAW-1", priority="MEDIA", quantity=9),
        ],
        capacities={"shared_component_pressure": True, "station_queue_pressure": 10},
    )
    # Near-tie: blocked boundary in top-K — 1 feasible + 2 blocked very close otherwise
    near_tie_blocked_boundary = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="NT_B_F", station="ZAW-1", priority="MEDIA", quantity=2),
            AtlasOrder(order_id="NT_B_B1", station="ZAW-1", priority="MEDIA", status="bloccato", quantity=2),
            AtlasOrder(order_id="NT_B_B2", station="ZAW-1", priority="MEDIA", status="bloccato", quantity=2),
        ],
    )
    return [
        ("baseline_feasible_mix", base),
        ("blocked_pressure", blocked),
        ("shared_component_pressure", shared),
        ("assembly_group", group),
        ("open_event_pressure", open_evt),
        ("near_tie_priority_vs_event", near_tie_priority_event),
        ("near_tie_shared_vs_station_pressure", near_tie_shared_station),
        ("near_tie_blocked_boundary", near_tie_blocked_boundary),
    ]


def run_grid(req: AtlasScenarioRequest, adapter: str = "ortools") -> str:
    baseline_cfg = PenaltyConfig()
    base_seq, base_meta = solve_req(req, baseline_cfg, adapter=adapter)

    feas_map = {o.order_id: (str(o.status or "").lower() != "bloccato") for o in req.orders}
    code_map = {o.order_id: (o.code or "") for o in req.orders}

    lines: List[str] = []
    m1, m3 = margins_top(base_meta, base_seq)
    lines.append(
        f"  [{adapter}] base: top1={base_seq[0] if base_seq else '-'} seq={base_seq} | margin_top1={m1:.3f} margin_top3_min={m3:.3f}"
    )

    def report(label: str, cfg: PenaltyConfig):
        seq, meta = solve_req(req, cfg, adapter=adapter)
        t1 = int(seq[0] != base_seq[0]) if seq and base_seq else 0
        h3 = hamming_at_k(base_seq, seq, 3)
        h5 = hamming_at_k(base_seq, seq, 5)
        sw = swap_count(base_seq, seq)
        viol = blocked_topk_violations(seq, feas_map, cfg)
        incoh = assembly_incoherence(seq, code_map)
        mt1, mt3 = margins_top(meta, seq)
        risk = near_flip_risk(meta, seq, k=3, eps=0.5)
        flag = " [Δ]" if (t1 or h3 or h5 or sw or viol or incoh) else ""
        lines.append(
            f"  [{adapter}] {label:28s} | top1_changed={t1} h3={h3} h5={h5} swaps={sw} blocked_topk={viol} incoh={incoh} "
            f"| margin_top1={mt1:.3f} margin_top3_min={mt3:.3f} risk@3<{0.5}={risk}{flag}"
        )

    # Variazioni fini: ±2%, ±5%, ±10%, ±15%
    factors = [0.98, 1.02, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15]
    for f in factors:
        report(
            f"blocked_penalty×{f}",
            replace(baseline_cfg, blocked_penalty=baseline_cfg.blocked_penalty * f),
        )
    for f in factors:
        report(
            f"shared_comp_penalty×{f}",
            replace(baseline_cfg, shared_component_penalty=baseline_cfg.shared_component_penalty * f),
        )
    for f in factors:
        report(
            f"assembly_coh_penalty×{f}",
            replace(baseline_cfg, assembly_coherence_penalty=baseline_cfg.assembly_coherence_penalty * f),
        )
    for f in factors:
        report(
            f"station_press_penalty×{f}",
            replace(baseline_cfg, station_pressure_penalty=baseline_cfg.station_pressure_penalty * f),
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS ranking stability micro-benchmark")
    parser.add_argument("--adapter", choices=["ortools", "pyomo", "both"], default="ortools")
    args = parser.parse_args()

    probes = make_probes()
    print("ATLAS Ranking Stability — local micro-benchmark")
    print("(backend-only, deterministic model, no DB/API changes)\n")
    for name, req in probes:
        print(f"dataset: {name}")
        if args.adapter in ("ortools", "both"):
            print(run_grid(req, adapter="ortools"))
        if args.adapter in ("pyomo", "both"):
            print(run_grid(req, adapter="pyomo"))
        print()


if __name__ == "__main__":
    main()
