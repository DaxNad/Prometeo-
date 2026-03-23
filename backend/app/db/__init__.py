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


def init_db() -> None:
    if current_backend() == "postgres":
        return

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
        conn.commit()
