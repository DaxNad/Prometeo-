from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class SequencePlannerService:
    """
    Planner iniziale PROMETEO.
    Primo strato Python sopra le viste SQL ZAW-1.

    Obiettivi attuali:
    - leggere la board operativa TL
    - produrre una global sequence runtime coerente
    - persistere global_sequence.json
    - produrre un primo turn_plan.json minimale
    """

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.global_sequence_file = self.data_dir / "global_sequence.json"
        self.turn_plan_file = self.data_dir / "turn_plan.json"

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

        return [dict(row) for row in rows]

    def build_global_sequence(self, db: Session) -> dict[str, Any]:
        board_rows = self.fetch_zaw1_board(db)

        sequence_items: list[dict[str, Any]] = []

        for row in board_rows:
            sequence_items.append(
                {
                    "rank": int(row["priorita_operativa"]),
                    "article": str(row["articolo"]),
                    "shared_components": self._split_components(row["componenti_condivisi"]),
                    "quantity": int(row["quantita"] or 0),
                    "due_date": (
                        row["data_spedizione"].isoformat()
                        if row["data_spedizione"] is not None
                        else None
                    ),
                    "customer_priority": row["priorita_cliente"],
                    "assembly_group": row["complessivo_articolo"],
                    "critical_station": row["postazione_critica"],
                    "tl_action": row["azione_tl"],
                    "logic_origin": row["origine_logica"],
                }
            )

        payload = {
            "planner_stage": "ZAW1_SQL_BRIDGE",
            "source_view": "vw_tl_zaw1_board",
            "items_count": len(sequence_items),
            "items": sequence_items,
        }

        self.save_global_sequence(payload)
        return payload

    def build_turn_plan(self, db: Session) -> dict[str, Any]:
        sequence = self.build_global_sequence(db)
        items = sequence.get("items", [])

        assignments: list[dict[str, Any]] = []

        for item in items:
            assignments.append(
                {
                    "slot": int(item["rank"]),
                    "shift": "DA_DEFINIRE",
                    "team_leader": "DA_DEFINIRE",
                    "station": item["critical_station"],
                    "article": item["article"],
                    "quantity": item["quantity"],
                    "shared_components": item["shared_components"],
                    "due_date": item["due_date"],
                    "customer_priority": item["customer_priority"],
                    "tl_action": item["tl_action"],
                    "planning_status": "BOZZA_INIZIALE",
                    "planning_origin": "GLOBAL_SEQUENCE",
                }
            )

        payload = {
            "planner_stage": "TURN_PLAN_STAGE_0",
            "source": "global_sequence.json",
            "assignments_count": len(assignments),
            "assignments": assignments,
        }

        self.save_turn_plan(payload)
        return payload

    def save_global_sequence(self, payload: dict[str, Any]) -> None:
        self.global_sequence_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_global_sequence(self) -> dict[str, Any]:
        if not self.global_sequence_file.exists():
            return {
                "planner_stage": "ZAW1_SQL_BRIDGE",
                "source_view": "vw_tl_zaw1_board",
                "items_count": 0,
                "items": [],
            }

        return json.loads(self.global_sequence_file.read_text(encoding="utf-8"))

    def save_turn_plan(self, payload: dict[str, Any]) -> None:
        self.turn_plan_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_turn_plan(self) -> dict[str, Any]:
        if not self.turn_plan_file.exists():
            return {
                "planner_stage": "TURN_PLAN_STAGE_0",
                "source": "global_sequence.json",
                "assignments_count": 0,
                "assignments": [],
            }

        return json.loads(self.turn_plan_file.read_text(encoding="utf-8"))

    def _split_components(self, raw_value: Any) -> list[str]:
        if raw_value is None:
            return []

        value = str(raw_value).strip()
        if not value:
            return []

        return [part.strip() for part in value.split("|") if part.strip()]


sequence_planner_service = SequencePlannerService()
