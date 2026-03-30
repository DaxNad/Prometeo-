from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class SequencePlannerService:

    SHIFT_SEQUENCE = ["NOTTE", "MATTINA", "POMERIGGIO"]

    TEAM_LEADERS = ["Davide", "Stefano", "Nino"]

    ROTATION_LOGIC = "SHIFT_TL_MULTI_CLUSTER"

    def __init__(self) -> None:

        base_dir = Path(__file__).resolve().parent.parent

        self.data_dir = base_dir / "data"

        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.global_sequence_file = self.data_dir / "global_sequence.json"

        self.turn_plan_file = self.data_dir / "turn_plan.json"


    # -------------------------

    def fetch_zaw1_board(self, db: Session) -> list[dict[str, Any]]:

        rows = db.execute(
            text(
                """
                SELECT
                    priorita_operativa,
                    articolo,
                    componenti_condivisi,
                    quantita,
                    data_spedizione,
                    priorita_cliente,
                    complessivo_articolo,
                    postazione_critica,
                    azione_tl,
                    origine_logica
                FROM vw_tl_zaw1_board
                ORDER BY priorita_operativa ASC
                """
            )
        ).mappings().all()

        return [dict(r) for r in rows]


    # -------------------------

    def build_global_sequence(self, db: Session):

        rows = self.fetch_zaw1_board(db)

        items = []

        for r in rows:

            items.append(
                {
                    "rank": int(r["priorita_operativa"]),
                    "article": str(r["articolo"]),
                    "shared_components": self._split(r["componenti_condivisi"]),
                    "quantity": int(r["quantita"] or 0),
                    "due_date": (
                        r["data_spedizione"].isoformat()
                        if r["data_spedizione"]
                        else None
                    ),
                    "customer_priority": r["priorita_cliente"],
                    "assembly_group": r["complessivo_articolo"],
                    "critical_station": r["postazione_critica"],
                    "tl_action": r["azione_tl"],
                    "logic_origin": r["origine_logica"],
                }
            )

        payload = {
            "planner_stage": "ZAW1_SQL_BRIDGE",
            "items_count": len(items),
            "items": items,
        }

        self._save(self.global_sequence_file, payload)

        return payload


    # -------------------------

    def build_turn_plan(self, db: Session):

        sequence = self.build_global_sequence(db)

        items = sequence["items"]

        today = date.today()

        base_rotation = today.toordinal() % len(self.SHIFT_SEQUENCE)

        clusters = self._cluster(items)

        assignments = []

        rotation_pointer = base_rotation

        for cluster in clusters:

            shift = self.SHIFT_SEQUENCE[rotation_pointer]

            tl = self.TEAM_LEADERS[rotation_pointer]

            for item in cluster:

                assignments.append(
                    {
                        "slot": item["rank"],

                        "plan_date": today.isoformat(),

                        "shift": shift,

                        "team_leader": tl,

                        "station": item["critical_station"],

                        "article": item["article"],

                        "quantity": item["quantity"],

                        "shared_components": item["shared_components"],

                        "due_date": item["due_date"],

                        "customer_priority": item["customer_priority"],

                        "tl_action": item["tl_action"],

                        "cluster_key": self._cluster_key(item),

                        "planning_status": "ASSEGNATO_MULTI_CLUSTER",

                        "planning_origin": "GLOBAL_SEQUENCE",
                    }
                )

            rotation_pointer = (
                rotation_pointer + 1
            ) % len(self.SHIFT_SEQUENCE)

        assignments.sort(key=lambda x: x["slot"])

        payload = {
            "planner_stage": "TURN_PLAN_STAGE_4",

            "rotation_logic": self.ROTATION_LOGIC,

            "plan_date": today.isoformat(),

            "clusters_count": len(clusters),

            "assignments_count": len(assignments),

            "assignments": assignments,
        }

        self._save(self.turn_plan_file, payload)

        return payload


    # -------------------------

    def _cluster(self, items):

        groups = defaultdict(list)

        for i in items:

            groups[self._cluster_key(i)].append(i)

        clusters = []

        for g in groups.values():

            g.sort(key=lambda x: x["rank"])

            clusters.append(g)

        clusters.sort(key=lambda g: min(x["rank"] for x in g))

        return clusters


    # -------------------------

    def _cluster_key(self, item):

        return (
            item["critical_station"],
            tuple(sorted(item["shared_components"]))
        )


    # -------------------------

    def _split(self, raw):

        if not raw:

            return []

        return [x.strip() for x in str(raw).split("|") if x.strip()]


    # -------------------------

    def _save(self, path, payload):

        path.write_text(

            json.dumps(payload, indent=2, ensure_ascii=False)

        )


sequence_planner_service = SequencePlannerService()
