from __future__ import annotations

from typing import List, Tuple, Optional
from dataclasses import dataclass

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from ..constants import PRIORITY_WEIGHTS
from .base import BaseAdapter


@dataclass
class PenaltyConfig:
    blocked_penalty: float = 100.0
    shared_component_penalty: float = 1.0
    open_event_penalty: float = 1.0
    station_pressure_penalty: float = 0.1  # multiplier on (pressure_level * quantity)
    assembly_coherence_penalty: float = 0.01  # per position inside group baseline
    # soft top-k blocked limiter
    max_blocked_in_top_k: int = 1
    top_k_window: int = 3
    blocked_excess_penalty: float = 5.0


class ORToolsAdapter(BaseAdapter):
    def __init__(self, config: Optional[PenaltyConfig] = None) -> None:
        self._cfg = config or PenaltyConfig()
    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        """Deterministic solve with minimal OR-Tools model (v0).

        Notes
        - No DB access.
        - Feasible-first: non-bloccati prima dei bloccati.
        - Penalità evento OPEN sulla station critica (globale, informativa).
        - Penalità pressione componenti condivisi se specificata in capacities.values.
        - Pesi priorità cliente (ALTA>MEDIA>BASSA) da constants.PRIORITY_WEIGHTS.
        - Tie-break stabile su order_id.
        """

        # Signals (global, non cambiano l'ordinamento relativo se uniformi)
        has_open_event = any(e.status == "OPEN" for e in snapshot.events)
        shared_pressure = bool(snapshot.capacities.values.get("shared_component_pressure", False))

        # Costruisco pesi deterministici per ogni ordine (Model v1) con breakdown
        weights: List[Tuple[float, str, bool, dict, str]] = []  # (w_i, order_id, feasible, breakdown, group_key)
        cfg = self._cfg
        station_pressure_level = 0.0
        sp_val = snapshot.capacities.values.get("station_queue_pressure") if snapshot.capacities else 0
        try:
            station_pressure_level = float(sp_val or 0)
        except Exception:
            station_pressure_level = 1.0 if bool(sp_val) else 0.0
        for o in snapshot.orders:
            feasible = str(o.status or "").lower() != "bloccato"
            prio = PRIORITY_WEIGHTS.get(str(o.priority or "").upper(), 0)
            # componenti obiettivo
            priority_reward = prio * 10.0
            blocked_penalty = 0.0 if feasible else cfg.blocked_penalty
            shared_component_penalty = cfg.shared_component_penalty if shared_pressure else 0.0
            open_event_penalty = cfg.open_event_penalty if has_open_event else 0.0
            # penalità proporzionale alla quantità per riflettere la pressione di coda
            station_pressure_penalty = station_pressure_level * float(o.quantity or 0) * cfg.station_pressure_penalty

            w = priority_reward - blocked_penalty - shared_component_penalty - open_event_penalty - station_pressure_penalty
            breakdown = {
                "order_id": o.order_id,
                "priority_reward": priority_reward,
                "blocked_penalty": blocked_penalty,
                "shared_component_penalty": shared_component_penalty,
                "open_event_penalty": open_event_penalty,
                "station_pressure_penalty": station_pressure_penalty,
                "total": w,
            }
            group_key = str(o.code or "")  # assembly_group coherence via code convention
            weights.append((w, o.order_id, feasible, breakdown, group_key))

        # Coerenza assembly_group (soft): penalità crescente per posizione nel baseline del gruppo
        # Baseline per gruppo: ordinamento per punteggio base desc e order_id
        groups: dict[str, List[Tuple[float, str, bool, dict, str]]] = {}
        for entry in weights:
            _w, _oid, _feas, _bd, g = entry
            if not g:
                continue
            groups.setdefault(g, []).append(entry)
        if groups:
            new_weights: List[Tuple[float, str, bool, dict, str]] = []
            index_map: dict[str, int] = {}
            for gk, items in groups.items():
                items_sorted = sorted(items, key=lambda t: (-t[0], t[1]))
                for pos, (w0, oid0, feas0, bd0, g0) in enumerate(items_sorted):
                    penalty = pos * cfg.assembly_coherence_penalty
                    w_adj = w0 - penalty
                    bd0["total"] = w_adj
                    index_map[oid0] = 1  # mark handled
                    new_weights.append((w_adj, oid0, feas0, bd0, g0))
            # add items with no group or singletons
            for (w0, oid0, feas0, bd0, g0) in weights:
                if not g0 or oid0 not in index_map:
                    new_weights.append((w0, oid0, feas0, bd0, g0))
            weights = new_weights

        # Soft limiter: penalizza i bloccati in eccesso nelle prime K posizioni (baseline attuale)
        if cfg.top_k_window > 0 and cfg.max_blocked_in_top_k >= 0 and cfg.blocked_excess_penalty != 0:
            baseline = sorted(weights, key=lambda t: (-t[0], t[1]))
            blocked_seen = 0
            updated: dict[str, float] = {}
            updated_bd: dict[str, dict] = {}
            for pos, (w0, oid0, feas0, bd0, g0) in enumerate(baseline[: cfg.top_k_window]):
                if not feas0:
                    blocked_seen += 1
                    if blocked_seen > cfg.max_blocked_in_top_k:
                        extra = (blocked_seen - cfg.max_blocked_in_top_k) * cfg.blocked_excess_penalty
                        neww = w0 - extra
                        newbd = dict(bd0)
                        newbd["blocked_penalty"] = float(newbd.get("blocked_penalty", 0.0)) + extra
                        newbd["total"] = neww
                        updated[oid0] = neww
                        updated_bd[oid0] = newbd
            if updated:
                new_weights: List[Tuple[float, str, bool, dict, str]] = []
                for (w0, oid0, feas0, bd0, g0) in weights:
                    if oid0 in updated:
                        new_weights.append((updated[oid0], oid0, feas0, updated_bd[oid0], g0))
                    else:
                        new_weights.append((w0, oid0, feas0, bd0, g0))
                weights = new_weights

        # Provo a usare OR-Tools CP-SAT per selezionare elementi (x_i ∈ {0,1})
        used_cp = False
        x_selected: List[Tuple[int, float, str]] = []  # (x_i, w_i, order_id)
        try:
            from ortools.sat.python import cp_model  # type: ignore

            model = cp_model.CpModel()
            xs = []
            coeffs = []
            for idx, (w, oid, _feas, _bd, _g) in enumerate(weights):
                x = model.NewBoolVar(f"x_{idx}_{oid}")
                xs.append(x)
                # CP-SAT usa coefficienti interi, scalare i pesi
                coeffs.append(int(round(w * 100)))

            # Massimizzo sum(w_i * x_i)
            model.Maximize(sum(c * x for c, x in zip(coeffs, xs)))

            # Risolvo con un solo worker per determinismo
            solver = cp_model.CpSolver()
            solver.parameters.num_search_workers = 1
            solver.parameters.max_time_in_seconds = 2.0
            res = solver.Solve(model)
            if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                raise RuntimeError("ORTools returned infeasible/unbounded")

            for (w, oid, _feas, _bd, _g), x in zip(weights, xs):
                x_selected.append((int(solver.Value(x)), w, oid))
            used_cp = True
        except Exception:
            # Nessun OR-Tools o errore: fallback interno all'adapter (non orchestrator)
            for (w, oid, _feas, _bd, _g) in weights:
                x_selected.append((1 if w >= 0 else 0, w, oid))

        # Ordino: selezionati prima (x=1), poi per peso desc, poi order_id asc
        x_selected.sort(key=lambda t: (-t[0], -t[1], t[2]))
        sequence = [oid for _, _, oid in x_selected]

        # Hard rule (minima): se esiste almeno un feasible, il primo non può essere bloccato
        feasibles = {oid for (_, _, oid), (_w, _oid, feas, _bd, _g) in zip(x_selected, weights) if feas}
        if sequence:
            first_oid = sequence[0]
            # trova feasibility della prima
            first_is_blocked = False
            for (_w, oid, feas, _bd, _g) in weights:
                if oid == first_oid:
                    first_is_blocked = not feas
                    break
            if first_is_blocked and any(oid in feasibles for oid in sequence[1:]):
                # sposta in testa il miglior feasible per peso (deterministico)
                # ricostruisco mappa pesi
                wmap = {oid: w for (w, oid, _feas, _bd, _g) in weights}
                feasible_candidates = [oid for oid in sequence if oid in feasibles]
                feasible_candidates.sort(key=lambda oid: (-wmap.get(oid, -1e9), oid))
                best = feasible_candidates[0]
                sequence = [best] + [oid for oid in sequence if oid != best]

        # Post-process: sposta sempre i bloccati in fondo mantenendo l'ordine relativo
        feas_map = {oid: feas for (_w, oid, feas, _bd, _g) in weights}
        feas_order = [oid for oid in sequence if feas_map.get(oid, False)]
        blocked_order = [oid for oid in sequence if not feas_map.get(oid, False)]
        sequence = feas_order + blocked_order

        # score breakdown per item (ordinato per sequenza)
        bmap = {bd["order_id"]: bd for (_w, _oid, _feas, bd, _g) in weights}
        scores = [bmap.get(oid, {}) for oid in sequence]

        meta = {
            "adapter": "ortools",
            "solver": "cp-sat" if used_cp else "pure-scoring",
            "scoring": {
                "feasible_first": True,
                "priority_weights": PRIORITY_WEIGHTS,
                "penalty_open_event": has_open_event,
                "penalty_shared_pressure": shared_pressure,
                "station_queue_pressure": station_pressure_level,
            },
            "scores": scores,
        }
        return {"sequence": sequence, "meta": meta}
