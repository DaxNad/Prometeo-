from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..station_normalizer import normalize_station
from app.agent_runtime.service import AgentRuntimeService
from app.services.component_usage_service import build_component_usage_from_db, apply_component_impact, get_component_conflicts
from app.services.component_usage_service import build_component_usage_from_db, apply_component_impact
from app.domain.article_profile_resolver import resolve_article_profile
from app.domain.operational_class import build_planner_admission_gate
from app.domain.drawing_registry_service import override_postazioni_from_registry


class SequencePlannerService:
    SHIFT_SEQUENCE = ["NOTTE", "MATTINA", "POMERIGGIO"]
    TEAM_LEADERS = ["Davide", "Stefano", "Nino"]
    ROTATION_LOGIC = "SHIFT_TL_MULTI_CLUSTER"

    PRIORITY_RANK = {
        "CRITICA": 0,
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

        self.agent_runtime = AgentRuntimeService()

    def fetch_station_board(self, db: Session, view_name: str) -> list[dict[str, Any]]:
        sql = f"""
            SELECT
                priorita_operativa,
                articolo,
                disegno,
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
        rows = db.execute(text(sql)).mappings().all()
        return [dict(r) for r in rows]

    def fetch_global_board(self, db: Session) -> list[dict[str, Any]]:
        combined: list[dict[str, Any]] = []

        for source in self.BOARD_SOURCES:
            view_name = source["view"]
            rows = self.fetch_station_board(db, view_name)

            for row in rows:
                item = dict(row)
                item["_source_view"] = view_name
                combined.append(item)

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

    def build_global_sequence(self, db: Session) -> dict[str, Any]:
        rows = self.fetch_global_board(db)
        open_events = _get_open_events_by_station(db)

        items: list[dict[str, Any]] = []
        for r in rows:
            article_code = str(r["articolo"])
            drawing = str(r.get("disegno") or "").strip()
            profile = resolve_article_profile(article_code)
            signals: dict[str, Any] = {}
            if profile:
                profile_signals = profile.get("signals", {})
                if isinstance(profile_signals, dict):
                    signals.update(profile_signals)

            critical_station = normalize_station(r["postazione_critica"])

            if drawing:
                overridden = override_postazioni_from_registry(
                    drawing=drawing,
                    inferred_postazioni=[critical_station],
                )
                if overridden:
                    critical_station = normalize_station(overridden[0])

            event_data = open_events.get(critical_station, {})
            open_events_total = int(event_data.get("open_events", 0) or 0)
            event_titles = str(event_data.get("titles", "") or "")

            customer_priority = r["priorita_cliente"]
            tl_action = r["azione_tl"]

            if open_events_total > 0:
                tl_action = "VERIFICA_SEGNALAZIONE_OPERATIVA"

            admission_profile = dict(profile or {})
            admission_profile.update(
                {
                    "article": article_code,
                    "active_lot": int(r["quantita"] or 0) > 0,
                    "explicit_operational_request": True,
                    "has_blocking_constraint": open_events_total > 0,
                }
            )
            admission = build_planner_admission_gate(admission_profile)

            items.append(
                {
                    "article": article_code,
                    "drawing": drawing,
                    "shared_components": self._split(r["componenti_condivisi"]),
                    "quantity": int(r["quantita"] or 0),
                    "due_date": (
                        r["data_spedizione"].isoformat()
                        if r["data_spedizione"]
                        else None
                    ),
                    "customer_priority": customer_priority,
                    "assembly_group": r["complessivo_articolo"],
                    "critical_station": critical_station,
                    "tl_action": tl_action,
                    "logic_origin": r["origine_logica"],
                    "source_view": r["_source_view"],
                    "station_rank": int(r["priorita_operativa"] or 0),
                    "open_events_total": open_events_total,
                    "event_titles": event_titles,
                    "event_impact": open_events_total > 0,
                    "planner_eligible": admission["planner_eligible"],
                    "planner_admitted": admission["planner_admitted"],
                    "admission_reasons": admission["reasons"],
                    "human_override_allowed": admission["human_override_allowed"],
                    "planner_admission_rule": admission["rule"],
                    "signals": signals,
                }
            )

        items.sort(
            key=lambda item: (
                self._priority_value(item.get("customer_priority")),
                not item.get("shared_component_impact", False),
                item.get("due_date") or "9999-12-31",
                str(item.get("critical_station") or ""),
                int(item.get("station_rank") or 999999),
                str(item.get("article") or ""),
            )
        )

        ranked_items: list[dict[str, Any]] = []
        for idx, item in enumerate(items, start=1):
            ranked_item = dict(item)
            ranked_item["rank"] = idx
            ranked_items.append(ranked_item)

        
        # COMPONENT USAGE DA DB (cross-articolo reale)
        usage = build_component_usage_from_db(db)
        ranked_items = apply_component_impact(ranked_items, usage)

        payload = {
            "planner_stage": "ZAW_MULTI_SQL_EVENT_AWARE",
            "source_view": "+".join(source["view"] for source in self.BOARD_SOURCES),
            "items_count": len(ranked_items),
            "items": ranked_items,
            "warnings": self._build_warnings(ranked_items),
        }

        self._save(self.global_sequence_file, payload)

        self._agent_monitor(
            source="sequence_planner",
            line_id="planner",
            event_type="build_global_sequence",
            severity="info",
            payload={
                "planner_stage": payload["planner_stage"],
                "items_count": payload["items_count"],
                "source_view": payload["source_view"],
                "warnings": payload["warnings"],
            },
        )

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
                        "station": normalize_station(item["critical_station"]),
                        "article": item["article"],
                        "drawing": item.get("drawing", ""),
                        "quantity": item["quantity"],
                        "shared_components": item["shared_components"],
                        "due_date": item["due_date"],
                        "customer_priority": item["customer_priority"],
                        "tl_action": item["tl_action"],
                        "cluster_key": self._cluster_key(item),
                        "planning_status": "ASSEGNATO_MULTI_CLUSTER",
                        "planning_origin": "GLOBAL_SEQUENCE",
                        "source_view": item["source_view"],
                        "station_rank": item["station_rank"],
                        "open_events_total": item.get("open_events_total", 0),
                        "event_titles": item.get("event_titles", ""),
                        "event_impact": item.get("event_impact", False),
                        "planner_eligible": item.get("planner_eligible", False),
                        "planner_admitted": item.get("planner_admitted", False),
                        "admission_reasons": item.get("admission_reasons", []),
                        "human_override_allowed": item.get("human_override_allowed", True),
                        "planner_admission_rule": item.get("planner_admission_rule", ""),
                    }
                )

            rotation_pointer = (rotation_pointer + 1) % len(self.SHIFT_SEQUENCE)

        assignments.sort(key=lambda x: x["slot"])

        
        # COMPONENT USAGE DA DB (cross-articolo reale)
        usage = build_component_usage_from_db(db)
        assignments = apply_component_impact(assignments, usage)

        payload = {
            "planner_stage": "TURN_PLAN_STAGE_4_EVENT_AWARE",
            "source": "+".join(source["view"] for source in self.BOARD_SOURCES),
            "rotation_logic": self.ROTATION_LOGIC,
            "plan_date": today.isoformat(),
            "clusters_count": len(clusters),
            "assignments_count": len(assignments),
            "assignments": assignments,
            "warnings": sequence.get("warnings", []),
        }

        self._save(self.turn_plan_file, payload)

        self._agent_monitor(
            source="sequence_planner",
            line_id="planner",
            event_type="build_turn_plan",
            severity="info",
            payload={
                "planner_stage": payload["planner_stage"],
                "assignments_count": payload["assignments_count"],
                "clusters_count": payload["clusters_count"],
                "rotation_logic": payload["rotation_logic"],
                "warnings": payload["warnings"],
            },
        )

        return payload

    def _build_warnings(self, items: list[dict[str, Any]]) -> list[str]:
        impacted_stations: list[str] = []
        for item in items:
            if item.get("open_events_total", 0) > 0:
                station = str(item.get("critical_station") or "")
                if station and station not in impacted_stations:
                    impacted_stations.append(station)

        if not impacted_stations:
            return []

        return [
            "postazioni con segnalazioni operative aperte in sequenza: "
            + ", ".join(impacted_stations)
        ]

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

    def _agent_monitor(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> None:
        try:
            asyncio.run(
                self.agent_runtime.analyze(
                    source=source,
                    line_id=line_id,
                    event_type=event_type,
                    severity=severity,
                    payload=payload or {},
                )
            )
        except RuntimeError:
            pass
        except Exception:
            pass


sequence_planner_service = SequencePlannerService()


def _get_open_events_by_station(db: Session) -> dict[str, dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                """
                SELECT
                    station,
                    COUNT(*) AS open_events,
                    STRING_AGG(title, ' | ' ORDER BY opened_at DESC) AS titles
                FROM events
                WHERE status = 'OPEN'
                GROUP BY station
                """
            )
        ).mappings().all()
    except Exception:
        # relazione 'events' non disponibile: fallback safe
        rows = []

    result: dict[str, dict[str, Any]] = {}

    for r in rows:
        station = normalize_station(r["station"])
        result[station] = {
            "open_events": int(r["open_events"] or 0),
            "titles": str(r["titles"] or ""),
        }

    return result
