from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import text

from ..db.session import engine


class AgentRunRepository:
    def save(
        self,
        *,
        source: str,
        line_id: str,
        event_type: str,
        severity: str | None,
        inspection: dict[str, Any],
        decision_mode: str,
        action: str,
        explanation: str | None,
    ) -> None:
        inspection_json = json.dumps(inspection, ensure_ascii=False)

        stmt = text(
            """
            INSERT INTO agent_runs (
                source,
                line_id,
                event_type,
                severity,
                inspection_json,
                decision_mode,
                action,
                explanation
            )
            VALUES (
                :source,
                :line_id,
                :event_type,
                :severity,
                CAST(:inspection_json AS JSONB),
                :decision_mode,
                :action,
                :explanation
            )
            """
        )

        params = {
            "source": source,
            "line_id": line_id,
            "event_type": event_type,
            "severity": severity,
            "inspection_json": inspection_json,
            "decision_mode": decision_mode,
            "action": action,
            "explanation": explanation,
        }

        with engine.begin() as conn:
            conn.execute(stmt, params)

    def list_recent(
        self,
        *,
        line_id: str | None = None,
        action: str | None = None,
        decision_mode: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        filters: list[str] = []
        params: dict[str, Any] = {"limit": int(limit)}

        if line_id:
            filters.append("line_id = :line_id")
            params["line_id"] = line_id

        if action:
            filters.append("action = :action")
            params["action"] = action

        if decision_mode:
            filters.append("decision_mode = :decision_mode")
            params["decision_mode"] = decision_mode

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        stmt = text(
            f"""
            SELECT
                id,
                source,
                line_id,
                event_type,
                severity,
                inspection_json,
                decision_mode,
                action,
                explanation,
                created_at
            FROM agent_runs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(stmt, params).mappings().all()

        result: list[dict[str, Any]] = []
        for row in rows:
            created_at = row["created_at"]
            if isinstance(created_at, datetime):
                created_at_value = created_at.isoformat()
            else:
                created_at_value = str(created_at) if created_at is not None else None

            inspection_json = row["inspection_json"]
            if isinstance(inspection_json, str):
                try:
                    inspection_json = json.loads(inspection_json)
                except Exception:
                    inspection_json = {"raw": inspection_json}

            result.append(
                {
                    "id": row["id"],
                    "source": row["source"],
                    "line_id": row["line_id"],
                    "event_type": row["event_type"],
                    "severity": row["severity"],
                    "inspection_json": inspection_json,
                    "decision_mode": row["decision_mode"],
                    "action": row["action"],
                    "explanation": row["explanation"],
                    "created_at": created_at_value,
                }
            )

        return result

    def summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict[str, Any]:
        filters: list[str] = []
        params: dict[str, Any] = {}

        if line_id:
            filters.append("line_id = :line_id")
            params["line_id"] = line_id

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        stmt = text(
            f"""
            SELECT
                COUNT(*) AS total_runs,
                COUNT(*) FILTER (WHERE action = 'monitor') AS monitor_count,
                COUNT(*) FILTER (WHERE action = 'investigate') AS investigate_count,
                COUNT(*) FILTER (WHERE decision_mode = 'local-rule') AS local_rule_count,
                COUNT(*) FILTER (WHERE decision_mode = 'local-escalation') AS local_escalation_count,
                COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'order') AS order_domain_count,
                COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'machine') AS machine_domain_count,
                COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'legacy_bootstrap') AS legacy_bootstrap_count,
                COUNT(*) FILTER (WHERE inspection_json->>'possible_anomaly' = 'true') AS possible_anomaly_count,
                COUNT(*) FILTER (WHERE inspection_json->>'blocked_order' = 'true') AS blocked_order_count,
                COUNT(*) FILTER (WHERE inspection_json->>'overdue' = 'true') AS overdue_count
            FROM agent_runs
            {where_clause}
            """
        )

        with engine.connect() as conn:
            row = conn.execute(stmt, params).mappings().first()

        if not row:
            return {
                "line_id": line_id,
                "total_runs": 0,
                "monitor_count": 0,
                "investigate_count": 0,
                "local_rule_count": 0,
                "local_escalation_count": 0,
                "order_domain_count": 0,
                "machine_domain_count": 0,
                "legacy_bootstrap_count": 0,
                "possible_anomaly_count": 0,
                "blocked_order_count": 0,
                "overdue_count": 0,
            }

        return {
            "line_id": line_id,
            "total_runs": row["total_runs"],
            "monitor_count": row["monitor_count"],
            "investigate_count": row["investigate_count"],
            "local_rule_count": row["local_rule_count"],
            "local_escalation_count": row["local_escalation_count"],
            "order_domain_count": row["order_domain_count"],
            "machine_domain_count": row["machine_domain_count"],
            "legacy_bootstrap_count": row["legacy_bootstrap_count"],
            "possible_anomaly_count": row["possible_anomaly_count"],
            "blocked_order_count": row["blocked_order_count"],
            "overdue_count": row["overdue_count"],
        }

    def operational_summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict[str, Any]:
        filters = ["inspection_json->>'event_domain' IN ('order', 'legacy_bootstrap')"]
        params: dict[str, Any] = {}

        if line_id:
            filters.append("line_id = :line_id")
            params["line_id"] = line_id

        where_clause = "WHERE " + " AND ".join(filters)

        stmt = text(
            f"""
            SELECT
                COUNT(*) AS orders_total,
                COUNT(*) FILTER (WHERE action = 'monitor') AS orders_monitor,
                COUNT(*) FILTER (WHERE action = 'investigate') AS orders_investigate,
                COUNT(*) FILTER (
                    WHERE inspection_json->>'event_domain' = 'order'
                      AND action = 'monitor'
                      AND COALESCE(inspection_json->>'possible_anomaly', 'false') = 'false'
                ) AS orders_ok,
                COUNT(*) FILTER (
                    WHERE COALESCE(inspection_json->>'blocked_order', 'false') = 'true'
                ) AS orders_blocked,
                COUNT(*) FILTER (
                    WHERE COALESCE(inspection_json->>'overdue', 'false') = 'true'
                ) AS orders_overdue,
                COUNT(*) FILTER (
                    WHERE COALESCE(inspection_json->>'urgent_order', 'false') = 'true'
                ) AS orders_urgent,
                COUNT(*) FILTER (
                    WHERE inspection_json->>'event_domain' = 'legacy_bootstrap'
                ) AS legacy_bootstrap_count,
                COUNT(*) FILTER (
                    WHERE inspection_json->>'event_domain' = 'order'
                ) AS domain_order_count
            FROM agent_runs
            {where_clause}
            """
        )

        with engine.connect() as conn:
            row = conn.execute(stmt, params).mappings().first()

        if not row:
            return {
                "line_id": line_id,
                "orders_total": 0,
                "orders_monitor": 0,
                "orders_investigate": 0,
                "orders_ok": 0,
                "orders_blocked": 0,
                "orders_overdue": 0,
                "orders_urgent": 0,
                "legacy_bootstrap_count": 0,
                "domain_order_count": 0,
            }

        return {
            "line_id": line_id,
            "orders_total": row["orders_total"],
            "orders_monitor": row["orders_monitor"],
            "orders_investigate": row["orders_investigate"],
            "orders_ok": row["orders_ok"],
            "orders_blocked": row["orders_blocked"],
            "orders_overdue": row["orders_overdue"],
            "orders_urgent": row["orders_urgent"],
            "legacy_bootstrap_count": row["legacy_bootstrap_count"],
            "domain_order_count": row["domain_order_count"],
        }
