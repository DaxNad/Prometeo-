from __future__ import annotations

from typing import List, Tuple

from ..domain.snapshot import Snapshot
from ..types import ConstraintSet, ObjectiveSpec, SolveResult
from ..constants import PRIORITY_WEIGHTS
from .base import BaseAdapter


class ORToolsAdapter(BaseAdapter):
    def solve(self, snapshot: Snapshot, constraints: ConstraintSet, objective: ObjectiveSpec) -> SolveResult:  # noqa: D401
        """Deterministic scoring-based solve.

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

        scored: List[Tuple[float, str]] = []
        for o in snapshot.orders:
            feasible = str(o.status or "").lower() != "bloccato"
            prio = PRIORITY_WEIGHTS.get(str(o.priority or "").upper(), 0)

            # Scoring: grande margine alla fattibilità, poi priorità, poi piccole penalità globali
            score = 0.0
            score += 1000.0 if feasible else 0.0  # feasible-first
            score += prio * 10.0  # priorità cliente
            if has_open_event:
                score -= 1.0  # pressione operativa (globale)
            if shared_pressure:
                score -= 1.0  # pressione componenti condivisi (globale)

            # Ordine deterministico: score desc, poi order_id asc
            # Usiamo score negativo per ordinare crescentemente con chiave tuple
            scored.append((-score, o.order_id))

        scored.sort()
        sequence = [oid for _, oid in scored]
        meta = {
            "adapter": "ortools",
            "scoring": {
                "feasible_first": True,
                "priority_weights": PRIORITY_WEIGHTS,
                "penalty_open_event": has_open_event,
                "penalty_shared_pressure": shared_pressure,
            },
        }
        return {"sequence": sequence, "meta": meta}
