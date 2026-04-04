from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from ..config import settings


def current_backend() -> str:
    return settings.db_backend


def sqlite_db_path() -> Path:
    settings.sqlite_dir.mkdir(parents=True, exist_ok=True)
    return settings.sqlite_path


def get_sqlite_connection() -> sqlite3.Connection:
    path = sqlite_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_postgres_connection():
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL non configurato")
    return psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)


def get_connection() -> Any:
    if current_backend() == "postgres":
        return get_postgres_connection()
    return get_sqlite_connection()


def probe_postgres() -> dict:
    if not settings.database_url:
        return {
            "configured": False,
            "reachable": False,
            "message": "DATABASE_URL non configurato",
        }

    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok;")
                row = cur.fetchone()

        return {
            "configured": True,
            "reachable": True,
            "message": "Connessione PostgreSQL OK",
            "result": row,
        }
    except Exception as exc:
        return {
            "configured": True,
            "reachable": False,
            "message": str(exc),
        }


def _init_sqlite_schema() -> None:
    with get_sqlite_connection() as conn:
        conn.execute(
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
                opened_at TEXT NOT NULL,
                closed_at TEXT,
                closed_by TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                line_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT,
                inspection_json TEXT NOT NULL,
                decision_mode TEXT NOT NULL,
                action TEXT NOT NULL,
                explanation TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at
            ON agent_runs(created_at)
            """
        )

        conn.commit()


def _init_postgres_schema() -> None:
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id BIGSERIAL PRIMARY KEY,
                    source TEXT NOT NULL,
                    line_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NULL,
                    inspection_json JSONB NOT NULL,
                    decision_mode TEXT NOT NULL,
                    action TEXT NOT NULL,
                    explanation TEXT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at
                ON agent_runs(created_at DESC)
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_runs_line_id
                ON agent_runs(line_id)
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_runs_action
                ON agent_runs(action)
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_runs_decision_mode
                ON agent_runs(decision_mode)
                """
            )

        conn.commit()


def init_db() -> None:
    if current_backend() == "postgres":
        _init_postgres_schema()
        return

    _init_sqlite_schema()
