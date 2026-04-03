from __future__ import annotations

import json
import subprocess
from typing import Any


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
        inspection_json = json.dumps(inspection).replace("'", "''")
        source = (source or "").replace("'", "''")
        line_id = (line_id or "").replace("'", "''")
        event_type = (event_type or "").replace("'", "''")
        severity = (severity or "").replace("'", "''")
        decision_mode = (decision_mode or "").replace("'", "''")
        action = (action or "").replace("'", "''")
        explanation = (explanation or "").replace("'", "''")

        sql = f"""
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
            '{source}',
            '{line_id}',
            '{event_type}',
            '{severity}',
            '{inspection_json}'::jsonb,
            '{decision_mode}',
            '{action}',
            '{explanation}'
        );
        """

        subprocess.run(
            ["psql", "prometeo", "-c", sql],
            check=True,
            capture_output=True,
            text=True,
        )

    def list_recent(
        self,
        *,
        line_id: str | None = None,
        action: str | None = None,
        decision_mode: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        filters = []

        if line_id:
            safe_line_id = line_id.replace("'", "''")
            filters.append(f"line_id = '{safe_line_id}'")

        if action:
            safe_action = action.replace("'", "''")
            filters.append(f"action = '{safe_action}'")

        if decision_mode:
            safe_decision_mode = decision_mode.replace("'", "''")
            filters.append(f"decision_mode = '{safe_decision_mode}'")

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        sql = f"""
        SELECT json_build_object(
            'id', id,
            'source', source,
            'line_id', line_id,
            'event_type', event_type,
            'severity', severity,
            'inspection_json', inspection_json,
            'decision_mode', decision_mode,
            'action', action,
            'explanation', explanation,
            'created_at', to_char(created_at AT TIME ZONE 'Europe/Rome', 'YYYY-MM-DD"T"HH24:MI:SS')
        )
        FROM agent_runs
        {where_clause}
        ORDER BY created_at DESC
        LIMIT {int(limit)};
        """

        result = subprocess.run(
            ["psql", "prometeo", "-t", "-A", "-c", sql],
            check=True,
            capture_output=True,
            text=True,
        )

        rows: list[dict[str, Any]] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

        return rows

    def summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict[str, Any]:
        filters = []

        if line_id:
            safe_line_id = line_id.replace("'", "''")
            filters.append(f"line_id = '{safe_line_id}'")
            safe_line_value = "'" + safe_line_id + "'"
        else:
            safe_line_value = "NULL"

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        sql = f"""
        SELECT json_build_object(
            'line_id', {safe_line_value},
            'total_runs', COUNT(*),
            'monitor_count', COUNT(*) FILTER (WHERE action = 'monitor'),
            'investigate_count', COUNT(*) FILTER (WHERE action = 'investigate'),
            'local_rule_count', COUNT(*) FILTER (WHERE decision_mode = 'local-rule'),
            'local_escalation_count', COUNT(*) FILTER (WHERE decision_mode = 'local-escalation'),
            'order_domain_count', COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'order'),
            'machine_domain_count', COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'machine'),
            'legacy_bootstrap_count', COUNT(*) FILTER (WHERE inspection_json->>'event_domain' = 'legacy_bootstrap'),
            'possible_anomaly_count', COUNT(*) FILTER (WHERE inspection_json->>'possible_anomaly' = 'true'),
            'blocked_order_count', COUNT(*) FILTER (WHERE inspection_json->>'blocked_order' = 'true'),
            'overdue_count', COUNT(*) FILTER (WHERE inspection_json->>'overdue' = 'true')
        )
        FROM agent_runs
        {where_clause};
        """

        result = subprocess.run(
            ["psql", "prometeo", "-t", "-A", "-c", sql],
            check=True,
            capture_output=True,
            text=True,
        )

        output = result.stdout.strip()
        return json.loads(output) if output else {}

    def operational_summary(
        self,
        *,
        line_id: str | None = None,
    ) -> dict[str, Any]:
        filters = ["inspection_json->>'event_domain' IN ('order', 'legacy_bootstrap')"]

        if line_id:
            safe_line_id = line_id.replace("'", "''")
            filters.append(f"line_id = '{safe_line_id}'")
            safe_line_value = "'" + safe_line_id + "'"
        else:
            safe_line_value = "NULL"

        where_clause = "WHERE " + " AND ".join(filters)

        sql = f"""
        SELECT json_build_object(
            'line_id', {safe_line_value},
            'orders_total', COUNT(*),
            'orders_monitor', COUNT(*) FILTER (WHERE action = 'monitor'),
            'orders_investigate', COUNT(*) FILTER (WHERE action = 'investigate'),
            'orders_ok', COUNT(*) FILTER (
                WHERE inspection_json->>'event_domain' = 'order'
                  AND action = 'monitor'
                  AND COALESCE(inspection_json->>'possible_anomaly', 'false') = 'false'
            ),
            'orders_blocked', COUNT(*) FILTER (
                WHERE COALESCE(inspection_json->>'blocked_order', 'false') = 'true'
            ),
            'orders_overdue', COUNT(*) FILTER (
                WHERE COALESCE(inspection_json->>'overdue', 'false') = 'true'
            ),
            'orders_urgent', COUNT(*) FILTER (
                WHERE COALESCE(inspection_json->>'urgent_order', 'false') = 'true'
            ),
            'legacy_bootstrap_count', COUNT(*) FILTER (
                WHERE inspection_json->>'event_domain' = 'legacy_bootstrap'
            ),
            'domain_order_count', COUNT(*) FILTER (
                WHERE inspection_json->>'event_domain' = 'order'
            )
        )
        FROM agent_runs
        {where_clause};
        """

        result = subprocess.run(
            ["psql", "prometeo", "-t", "-A", "-c", sql],
            check=True,
            capture_output=True,
            text=True,
        )

        output = result.stdout.strip()
        return json.loads(output) if output else {}
