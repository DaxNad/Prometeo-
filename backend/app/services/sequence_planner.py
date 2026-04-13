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

    PRIORITY_RANK = {
        "ALTA": 1,
        "MEDIA": 2,
        "BASSA": 3,
    }

    BOARD_SOURCES = [
        {"view": "vw_tl_zaw1_board", "station": "ZAW-1"},
        {"view": "vw_tl_zaw2_board", "station": "ZAW-2"},
    ]

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.global_sequence_file = self.data_dir / "global_sequence.json"
        self.turn_plan_file = self.data_dir / "turn_plan.json"

    # ------------------------------------------------------------------
    # Lettura da viste SQL ZAW (percorso principale)
    # ------------------------------------------------------------------

    def fetch_station_board(self, db: Session, view_name: str) -> list[dict[str, Any]]:
        sql = f"""
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
            FROM {view_name}
            ORDER BY
                priorita_operativa ASC,
                data_spedizione ASC NULLS LAST,
                articolo ASC
        """
        try:
            rows = db.execute(text(sql)).mappings().all()
            return [dict(r) for r in rows]
        except Exception:
            # Vista non esistente o errore SQL: restituisce lista vuota
            # senza propagare l'eccezione al chiamante.
            db.rollback()
            return []

    def fetch_global_board(self, db: Session) -> list[dict[str, Any]]:
        combined: list[dict[str, Any]] = []

        for source in self.BOARD_SOURCES:
            view_name = source["view"]
            rows = self.fetch_station_board(db, view_name)

            for row in rows:
                item = dict(row)
                item["_source_view"] = view_name
                combined.append(item)

        # Fallback: se le viste non esistono o sono vuote legge board_state
        if not combined:
            combined = self._fetch_from_board_state(db)

        combined.sort(
            key=lambda r: (
                self._priority_value(r.get("priorita_cliente")),
                r.get("data_spedizione") or date.max,
                str(r.get("postazione_critica") or ""),
                int(r.get("priorita_operativa") or 999999),
                str(r.get("articolo") or ""),
            )
        )

        return combined

    # ------------------------------------------------------------------
    # Fallback: lettura diretta da board_state
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date_str(raw: Any) -> date | None:
        if not raw:
            return None
        s = str(raw).strip().split("T")[0]
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                from datetime import datetime
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _azione_tl_from_row(stato: str, semaforo: str) -> str:
        if semaforo == "ROSSO" or stato == "bloccato":
            return "AVVIO_IMMEDIATO"
        if stato == "in corso":
            return "MONITORARE"
        return "PREPARARE_CAMBIO_SERIE"

    def _fetch_from_board_state(self, db: Session) -> list[dict[str, Any]]:
        try:
            rows = db.execute(
                text(
                    """
                    SELECT order_id, cliente, codice, qta, postazione,
                           stato, semaforo, due_date, note
                    FROM board_state
                    ORDER BY
                        CASE UPPER(semaforo)
                            WHEN 'ROSSO'  THEN 1
                            WHEN 'GIALLO' THEN 2
                            ELSE 3
                        END,
                        due_date ASC NULLS LAST,
                        codice ASC
                    """
                )
            ).mappings().all()
        except Exception:
            db.rollback()
            return []

        result: list[dict[str, Any]] = []
        for i, r in enumerate(rows, start=1):
            semaforo = str(r["semaforo"] or "GIALLO").upper()
            stato = str(r["stato"] or "da fare").lower()
            due = self._parse_date_str(r["due_date"])

            priorita_op = 1 if semaforo == "ROSSO" else 2 if semaforo == "GIALLO" else 3

            result.append(
                {
                    "priorita_operativa": priorita_op,
                    "articolo": r["codice"],
                    "componenti_condivisi": "",
                    "quantita": int(r["qta"] or 0),
                    "data_spedizione": due,
                    "priorita_cliente": semaforo,
                    "complessivo_articolo": r["codice"],
                    "postazione_critica": r["postazione"],
                    "azione_tl": self._azione_tl_from_row(stato, semaforo),
                    "origine_logica": "board_state",
                    "_source_view": "board_state",
                }
            )

        return result

    # ------------------------------------------------------------------
    # Build sequence / turn plan
    # ------------------------------------------------------------------

    def build_global_sequence(self, db: Session) -> dict[str, Any]:
        rows = self.fetch_global_board(db)

        using_fallback = bool(rows) and all(
            r.get("_source_view") == "board_state" for r in rows
        )

        items: list[dict[str, Any]] = []
        for idx, r in enumerate(rows, start=1):
            items.append(
                {
                    "rank": idx,
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
                    "source_view": r["_source_view"],
                    "station_rank": int(r["priorita_operativa"] or 0),
                }
            )

        if using_fallback:
            planner_stage = "BOARD_STATE_FALLBACK"
            source_view = "board_state"
        else:
            planner_stage = "ZAW_MULTI_SQL_BRIDGE"
            source_view = "+".join(source["view"] for source in self.BOARD_SOURCES)

        payload = {
            "planner_stage": planner_stage,
            "source_view": source_view,
            "items_count": len(items),
            "items": items,
        }

        self._save(self.global_sequence_file, payload)
        return payload

    def build_turn_plan(self, db: Session) -> dict[str, Any]:
        sequence = self.build_global_sequence(db)
        items = sequence["items"]

        today = date.today()
        base_rotation = today.toordinal() % len(self.SHIFT_SEQUENCE)
        clusters = self._cluster(items)

        assignments: list[dict[str, Any]] = []
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
                        "planning_origin": sequence["planner_stage"],
                        "source_view": item["source_view"],
                        "station_rank": item["station_rank"],
                    }
                )

            rotation_pointer = (rotation_pointer + 1) % len(self.SHIFT_SEQUENCE)

        assignments.sort(key=lambda x: x["slot"])

        payload = {
            "planner_stage": "TURN_PLAN_STAGE_4",
            "source": sequence["source_view"],
            "rotation_logic": self.ROTATION_LOGIC,
            "plan_date": today.isoformat(),
            "clusters_count": len(clusters),
            "assignments_count": len(assignments),
            "assignments": assignments,
        }

        self._save(self.turn_plan_file, payload)
        return payload

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cluster(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

        for item in items:
            groups[self._cluster_key(item)].append(item)

        clusters: list[list[dict[str, Any]]] = []
        for group in groups.values():
            group.sort(key=lambda x: x["rank"])
            clusters.append(group)

        clusters.sort(key=lambda g: min(x["rank"] for x in g))
        return clusters

    def _cluster_key(self, item: dict[str, Any]) -> tuple[Any, ...]:
        return (
            item["critical_station"],
            tuple(sorted(item["shared_components"])),
        )

    def _split(self, raw: Any) -> list[str]:
        if raw is None:
            return []

        value = str(raw).strip()
        if not value:
            return []

        return [part.strip() for part in value.split("|") if part.strip()]

    def _priority_value(self, raw: Any) -> int:
        if raw is None:
            return 9

        key = str(raw).strip().upper()
        return self.PRIORITY_RANK.get(key, 9)

    def _save(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


sequence_planner_service = SequencePlannerService()

