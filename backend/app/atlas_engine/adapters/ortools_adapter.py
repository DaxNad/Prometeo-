from __future__ import annotations

from typing import List, Tuple

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from ..constants import PRIORITY_WEIGHTS
from .base import BaseAdapter


class ORToolsAdapter(BaseAdapter):
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

        # Costruisco pesi deterministici per ogni ordine
        weights: List[Tuple[float, str, bool]] = []  # (w_i, order_id, feasible)
        for o in snapshot.orders:
            feasible = str(o.status or "").lower() != "bloccato"
            prio = PRIORITY_WEIGHTS.get(str(o.priority or "").upper(), 0)
            w = 0.0
            w += prio * 10.0  # priorità
            if has_open_event:
                w -= 1.0  # penalità evento aperto
            if shared_pressure:
                w -= 1.0  # penalità pressione condivisa
            if not feasible:
                w -= 100.0  # penalità forte per bloccato
            weights.append((w, o.order_id, feasible))

        # Provo a usare OR-Tools CP-SAT per selezionare elementi (x_i ∈ {0,1})
        used_cp = False
        x_selected: List[Tuple[int, float, str]] = []  # (x_i, w_i, order_id)
        try:
            from ortools.sat.python import cp_model  # type: ignore

            model = cp_model.CpModel()
            xs = []
            coeffs = []
            for idx, (w, oid, _feas) in enumerate(weights):
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

            for (w, oid, _), x in zip(weights, xs):
                x_selected.append((int(solver.Value(x)), w, oid))
            used_cp = True
        except Exception:
            # Nessun OR-Tools o errore: fallback interno all'adapter (non orchestrator)
            for (w, oid, _feas) in weights:
                x_selected.append((1 if w >= 0 else 0, w, oid))

        # Ordino: selezionati prima (x=1), poi per peso desc, poi order_id asc
        x_selected.sort(key=lambda t: (-t[0], -t[1], t[2]))
        sequence = [oid for _, _, oid in x_selected]

        meta = {
            "adapter": "ortools",
            "solver": "cp-sat" if used_cp else "pure-scoring",
            "scoring": {
                "feasible_first": True,
                "priority_weights": PRIORITY_WEIGHTS,
                "penalty_open_event": has_open_event,
                "penalty_shared_pressure": shared_pressure,
            },
        }
        return {"sequence": sequence, "meta": meta}
