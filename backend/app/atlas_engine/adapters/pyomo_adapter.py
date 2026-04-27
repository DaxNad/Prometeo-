from __future__ import annotations

from typing import List, Tuple, Optional

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from .base import BaseAdapter

# Reuse the same penalty configuration used by OR-Tools adapter
from .ortools_adapter import PenaltyConfig  # noqa: F401
from .ortools_adapter import PenaltyConfig as _PenaltyConfig


class PyomoAdapter(BaseAdapter):
    def __init__(self, config: Optional[_PenaltyConfig] = None) -> None:
        self._cfg = config or _PenaltyConfig()

    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        """Deterministic LP-based scoring with Pyomo (v1).

        Falls back to pure-scoring if Pyomo/solver is unavailable.
        """

        cfg = self._cfg
        has_open_event = any(e.status == "OPEN" for e in snapshot.events)
        shared_pressure_value = snapshot.capacities.values.get("shared_component_pressure", 0)
        shared_pressure = bool(shared_pressure_value)

        # Station queue pressure level (float), tolerate missing/non-numeric
        sp_level = 0.0
        sp_val = snapshot.capacities.values.get("station_queue_pressure") if snapshot.capacities else 0
        try:
            sp_level = float(sp_val or 0)
        except Exception:
            sp_level = 1.0 if bool(sp_val) else 0.0

        # Build base weights and per-item metadata
        weights: List[Tuple[float, str, bool, dict, str]] = []  # (w, order_id, feasible, breakdown, group_key)
        for o in snapshot.orders:
            feas = str(o.status or "").lower() != "bloccato"
            prio = 0
            try:
                from ..constants import PRIORITY_WEIGHTS
            except Exception:
                PRIORITY_WEIGHTS = {"ALTA": 3, "MEDIA": 2, "BASSA": 1}  # fallback literal
            prio = PRIORITY_WEIGHTS.get(str(o.priority or "").upper(), 0)

            priority_reward = prio * 10.0
            blocked_penalty = 0.0 if feas else cfg.blocked_penalty
            shared_component_penalty = cfg.shared_component_penalty * float(shared_pressure_value or 0)
            open_event_penalty = cfg.open_event_penalty if has_open_event else 0.0
            station_pressure_penalty = sp_level * float(o.quantity or 0) * cfg.station_pressure_penalty

            w = priority_reward - blocked_penalty - shared_component_penalty - open_event_penalty - station_pressure_penalty
            bd = {
                "order_id": o.order_id,
                "priority_reward": priority_reward,
                "blocked_penalty": blocked_penalty,
                "shared_component_penalty": shared_component_penalty,
                "open_event_penalty": open_event_penalty,
                "station_pressure_penalty": station_pressure_penalty,
                "total": w,
            }
            group_key = str(o.code or "")
            weights.append((w, o.order_id, feas, bd, group_key))

        # Assembly coherence: tiny position penalty; lexicographic bonus to earliest id
        groups = {}
        for entry in weights:
            groups.setdefault(entry[4], []).append(entry)
        if any(g for g in groups if g):
            new_weights: List[Tuple[float, str, bool, dict, str]] = []
            seen = set()
            for gk, items in groups.items():
                if not gk:
                    continue
                items_sorted = sorted(items, key=lambda t: (-t[0], t[1]))
                min_oid = min((oid for (_w, oid, _feas, _bd, _g) in items_sorted), default=None)
                for pos, (w0, oid0, feas0, bd0, g0) in enumerate(items_sorted):
                    penalty = pos * cfg.assembly_coherence_penalty
                    bonus = (cfg.assembly_coherence_penalty * 0.5) if (min_oid and oid0 == min_oid) else 0.0
                    w_adj = w0 - penalty + bonus
                    bd0["total"] = w_adj
                    new_weights.append((w_adj, oid0, feas0, bd0, g0))
                    seen.add(oid0)
            for (w0, oid0, feas0, bd0, g0) in weights:
                if oid0 not in seen:
                    new_weights.append((w0, oid0, feas0, bd0, g0))
            weights = new_weights

        # Soft top-k limiter for blocked (same behavior as OR-Tools adapter)
        if cfg.top_k_window > 0 and cfg.max_blocked_in_top_k >= 0 and cfg.blocked_excess_penalty != 0:
            baseline = sorted(weights, key=lambda t: (-t[0], t[1]))
            blocked_seen = 0
            updated_w = {}
            updated_bd = {}
            for pos, (w0, oid0, feas0, bd0, g0) in enumerate(baseline[: cfg.top_k_window]):
                if not feas0:
                    blocked_seen += 1
                    if blocked_seen > cfg.max_blocked_in_top_k:
                        extra = (blocked_seen - cfg.max_blocked_in_top_k) * cfg.blocked_excess_penalty
                        neww = w0 - extra
                        nbd = dict(bd0)
                        nbd["blocked_penalty"] = float(nbd.get("blocked_penalty", 0.0)) + extra
                        nbd["total"] = neww
                        updated_w[oid0] = neww
                        updated_bd[oid0] = nbd
            if updated_w:
                weights = [
                    (updated_w.get(oid, w), oid, feas, updated_bd.get(oid, bd), g)
                    for (w, oid, feas, bd, g) in weights
                ]

        # Try Pyomo; fallback to simple scoring if unavailable
        used_pyomo = False
        x_selected: List[Tuple[int, float, str]] = []
        try:
            from pyomo.environ import Binary, ConcreteModel, Objective, Var, maximize, value
            from pyomo.opt import SolverFactory

            model = ConcreteModel()
            idxs = list(range(len(weights)))
            model.X = Var(idxs, domain=Binary)
            coeffs = [int(round(w * 100)) for (w, _oid, _feas, _bd, _g) in weights]
            model.obj = Objective(expr=sum(coeffs[i] * model.X[i] for i in idxs), sense=maximize)

            # Choose available solver deterministically
            solver = None
            for cand in ("appsi_highs", "glpk", "cbc"):
                try:
                    if SolverFactory(cand).available(False):
                        solver = SolverFactory(cand)
                        break
                except Exception:
                    continue
            if solver is None:
                raise RuntimeError("No Pyomo solver available")

            res = solver.solve(model, tee=False)
            # extract selection
            for i, (w, oid, _feas, _bd, _g) in enumerate(weights):
                try:
                    xval = int(round(value(model.X[i])))
                except Exception:
                    xval = 1 if w >= 0 else 0
                x_selected.append((xval, w, oid))
            used_pyomo = True
        except Exception:
            for (w, oid, _feas, _bd, _g) in weights:
                x_selected.append((1 if w >= 0 else 0, w, oid))

        # Order: selected first, then by weight desc, then by id
        x_selected.sort(key=lambda t: (-t[0], -t[1], t[2]))
        sequence = [oid for _, _, oid in x_selected]

        # Enforce blocked-last stability
        feas_map = {oid: feas for (w, oid, feas, _bd, _g) in weights}
        feas_part = [oid for oid in sequence if feas_map.get(oid, False)]
        blocked_part = [oid for oid in sequence if not feas_map.get(oid, False)]
        sequence = feas_part + blocked_part

        # score breakdown per item
        bmap = {bd["order_id"]: bd for (w, _oid, _feas, bd, _g) in weights}
        scores = [bmap.get(oid, {}) for oid in sequence]

        meta = {
            "adapter": "pyomo",
            "solver": "pyomo-lp" if used_pyomo else "pure-scoring",
            "scoring": {
                "penalty_open_event": has_open_event,
                "penalty_shared_pressure": shared_pressure,
                "station_queue_pressure": sp_level,
            },
            "scores": scores,
        }
        return {"sequence": sequence, "meta": meta}
