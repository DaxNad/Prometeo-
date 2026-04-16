from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from .events_repository import EventsRepository
from ..db import get_postgres_connection


class PostgresEventsRepository(EventsRepository):
    """Primary domain repository backed by PostgreSQL authority."""
    def ping(self) -> dict[str, Any]:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok;")
                row = cur.fetchone()

        return {
            "ok": True,
            "result": row,
        }

    def ensure_schema(self) -> None:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        line TEXT NOT NULL,
                        station TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        status TEXT NOT NULL,
                        note TEXT,
                        source TEXT,
                        opened_at TIMESTAMP NOT NULL,
                        closed_at TIMESTAMP NULL,
                        closed_by TEXT NULL
                    );
                    """
                )
            conn.commit()

    def list_events(self) -> list[dict[str, Any]]:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, title, line, station, event_type, severity, status,
                        note, source, opened_at, closed_at, closed_by
                    FROM events
                    ORDER BY opened_at DESC
                    """
                )
                rows = cur.fetchall()
        return [dict(row) for row in rows]

    def list_active_events(self) -> list[dict[str, Any]]:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, title, line, station, event_type, severity, status,
                        note, source, opened_at, closed_at, closed_by
                    FROM events
                    WHERE status = 'OPEN'
                    ORDER BY opened_at DESC
                    """
                )
                rows = cur.fetchall()
        return [dict(row) for row in rows]

    def create_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        item = {
            "id": str(uuid4()),
            "title": payload["title"].strip(),
            "line": payload["line"].strip(),
            "station": payload["station"].strip(),
            "event_type": payload["event_type"].strip(),
            "severity": payload["severity"],
            "status": "OPEN",
            "note": payload.get("note", "").strip(),
            "source": (payload.get("source", "manual") or "manual").strip(),
            "opened_at": now,
            "closed_at": None,
            "closed_by": None,
        }

        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (
                        id, title, line, station, event_type, severity, status,
                        note, source, opened_at, closed_at, closed_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item["id"],
                        item["title"],
                        item["line"],
                        item["station"],
                        item["event_type"],
                        item["severity"],
                        item["status"],
                        item["note"],
                        item["source"],
                        item["opened_at"],
                        item["closed_at"],
                        item["closed_by"],
                    ),
                )
            conn.commit()

        return self.get_event(item["id"])

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, title, line, station, event_type, severity, status,
                        note, source, opened_at, closed_at, closed_by
                    FROM events
                    WHERE id = %s
                    """,
                    (event_id,),
                )
                row = cur.fetchone()
        return dict(row) if row else None

    def update_event(self, event_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get_event(event_id)
        if current is None:
            return None

        updated = {
            "title": payload.get("title", current["title"]).strip() if payload.get("title") is not None else current["title"],
            "line": payload.get("line", current["line"]).strip() if payload.get("line") is not None else current["line"],
            "station": payload.get("station", current["station"]).strip() if payload.get("station") is not None else current["station"],
            "event_type": payload.get("event_type", current["event_type"]).strip() if payload.get("event_type") is not None else current["event_type"],
            "severity": payload.get("severity", current["severity"]),
            "status": payload.get("status", current["status"]),
            "note": payload.get("note", current["note"]).strip() if payload.get("note") is not None else (current["note"] or ""),
            "source": payload.get("source", current["source"]).strip() if payload.get("source") is not None else (current["source"] or "manual"),
            "closed_at": current["closed_at"],
            "closed_by": current["closed_by"],
        }

        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE events
                    SET title = %s,
                        line = %s,
                        station = %s,
                        event_type = %s,
                        severity = %s,
                        status = %s,
                        note = %s,
                        source = %s,
                        closed_at = %s,
                        closed_by = %s
                    WHERE id = %s
                    """,
                    (
                        updated["title"],
                        updated["line"],
                        updated["station"],
                        updated["event_type"],
                        updated["severity"],
                        updated["status"],
                        updated["note"],
                        updated["source"],
                        updated["closed_at"],
                        updated["closed_by"],
                        event_id,
                    ),
                )
            conn.commit()

        return self.get_event(event_id)

    def close_event(self, event_id: str, closed_by: str) -> dict[str, Any] | None:
        current = self.get_event(event_id)
        if current is None:
            return None

        if current["status"] == "CLOSED":
            return current

        now = datetime.utcnow()

        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE events
                    SET status = 'CLOSED',
                        closed_at = %s,
                        closed_by = %s
                    WHERE id = %s
                    """,
                    (now, closed_by, event_id),
                )
            conn.commit()

        return self.get_event(event_id)

    def close_events_by_line(self, line: str, closed_by: str) -> dict[str, Any]:
        now = datetime.utcnow()

        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id
                    FROM events
                    WHERE line = %s AND status = 'OPEN'
                    """,
                    (line,),
                )
                rows = cur.fetchall()
                ids = [row["id"] for row in rows]

                if ids:
                    cur.execute(
                        """
                        UPDATE events
                        SET status = 'CLOSED',
                            closed_at = %s,
                            closed_by = %s
                        WHERE line = %s AND status = 'OPEN'
                        """,
                        (now, closed_by, line),
                    )

            conn.commit()

        return {
            "line": line,
            "closed_count": len(ids),
            "closed_ids": ids,
        }

    def list_station_states(self) -> list[dict[str, Any]]:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH ranked AS (
                        SELECT
                            id,
                            title,
                            line,
                            station,
                            event_type,
                            severity,
                            status,
                            note,
                            source,
                            opened_at,
                            closed_at,
                            CASE
                                WHEN status = 'OPEN' THEN opened_at
                                ELSE COALESCE(closed_at, opened_at)
                            END AS updated_at,
                            ROW_NUMBER() OVER (
                                PARTITION BY line, station
                                ORDER BY
                                    CASE WHEN status = 'OPEN' THEN 0 ELSE 1 END,
                                    CASE severity
                                        WHEN 'CRITICAL' THEN 0
                                        WHEN 'HIGH' THEN 1
                                        WHEN 'MEDIUM' THEN 2
                                        WHEN 'LOW' THEN 3
                                        ELSE 4
                                    END,
                                    CASE
                                        WHEN status = 'OPEN' THEN opened_at
                                        ELSE COALESCE(closed_at, opened_at)
                                    END DESC
                            ) AS rn
                        FROM events
                    )
                    SELECT
                        id,
                        title,
                        line,
                        station,
                        event_type,
                        severity,
                        status,
                        note,
                        source,
                        updated_at
                    FROM ranked
                    WHERE rn = 1
                    """
                )
                rows = cur.fetchall()

        items = [dict(row) for row in rows]
        for item in items:
            item["event_id"] = item["id"]
            item["priority_score"] = (1000 if item["status"] == "OPEN" else 0) + {
                "CRITICAL": 400,
                "HIGH": 300,
                "MEDIUM": 200,
                "LOW": 100,
            }.get((item.get("severity") or "").upper(), 0)

        items.sort(
            key=lambda x: (
                0 if x["status"] == "OPEN" else 1,
                -x["priority_score"],
                x["line"],
                x["station"],
            )
        )
        return items

    def get_station_state(self, line: str, station: str) -> dict[str, Any] | None:
        items = self.list_station_states()
        for item in items:
            if item["line"] == line and item["station"] == station:
                return item
        return None
