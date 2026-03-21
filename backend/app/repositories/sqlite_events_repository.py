from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from .events_repository import EventsRepository
from ..db import get_sqlite_connection


class SQLiteEventsRepository(EventsRepository):
    def list_events(self) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM events
                ORDER BY datetime(opened_at) DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def list_active_events(self) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM events
                WHERE status = 'OPEN'
                ORDER BY datetime(opened_at) DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def create_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow().isoformat()
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

        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO events (
                    id, title, line, station, event_type, severity, status,
                    note, source, opened_at, closed_at, closed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        return item

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                "SELECT * FROM events WHERE id = ?",
                (event_id,),
            ).fetchone()

        return dict(row) if row else None

    def update_event(self, event_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get_event(event_id)
        if current is None:
            return None

        updated = {
            "id": current["id"],
            "title": payload.get("title", current["title"]).strip() if payload.get("title") is not None else current["title"],
            "line": payload.get("line", current["line"]).strip() if payload.get("line") is not None else current["line"],
            "station": payload.get("station", current["station"]).strip() if payload.get("station") is not None else current["station"],
            "event_type": payload.get("event_type", current["event_type"]).strip() if payload.get("event_type") is not None else current["event_type"],
            "severity": payload.get("severity", current["severity"]),
            "status": payload.get("status", current["status"]),
            "note": payload.get("note", current["note"]).strip() if payload.get("note") is not None else (current["note"] or ""),
            "source": payload.get("source", current["source"]).strip() if payload.get("source") is not None else (current["source"] or "manual"),
            "opened_at": current["opened_at"],
            "closed_at": current["closed_at"],
            "closed_by": current["closed_by"],
        }

        with get_sqlite_connection() as conn:
            conn.execute(
                """
                UPDATE events
                SET title = ?, line = ?, station = ?, event_type = ?, severity = ?,
                    status = ?, note = ?, source = ?, closed_at = ?, closed_by = ?
                WHERE id = ?
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
                    updated["id"],
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

        now = datetime.utcnow().isoformat()

        with get_sqlite_connection() as conn:
            conn.execute(
                """
                UPDATE events
                SET status = 'CLOSED',
                    closed_at = ?,
                    closed_by = ?
                WHERE id = ?
                """,
                (now, closed_by, event_id),
            )
            conn.commit()

        return self.get_event(event_id)

    def close_events_by_line(self, line: str, closed_by: str) -> dict[str, Any]:
        now = datetime.utcnow().isoformat()

        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id
                FROM events
                WHERE line = ? AND status = 'OPEN'
                """,
                (line,),
            ).fetchall()

            ids = [row["id"] for row in rows]

            if ids:
                conn.execute(
                    """
                    UPDATE events
                    SET status = 'CLOSED',
                        closed_at = ?,
                        closed_by = ?
                    WHERE line = ? AND status = 'OPEN'
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
        query = """
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
                END AS effective_ts,
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
                        datetime(
                            CASE
                                WHEN status = 'OPEN' THEN opened_at
                                ELSE COALESCE(closed_at, opened_at)
                            END
                        ) DESC
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
            effective_ts
        FROM ranked
        WHERE rn = 1
        """
        with get_sqlite_connection() as conn:
            rows = conn.execute(query).fetchall()

        items = [dict(row) for row in rows]
        for item in items:
            item["updated_at"] = item.pop("effective_ts", None)
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
