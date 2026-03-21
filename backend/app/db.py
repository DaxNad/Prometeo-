import os
from pathlib import Path
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings


DEFAULT_CREATE_EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'OPEN',
    title TEXT NOT NULL DEFAULT 'PROMETEO EVENT',
    area TEXT NOT NULL DEFAULT 'PROD',
    note TEXT NULL,
    code TEXT NULL,
    station TEXT NULL,
    shift TEXT NULL,
    closed_at TIMESTAMPTZ NULL,
    kind TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_events_ts_desc
    ON events (ts DESC);

CREATE INDEX IF NOT EXISTS idx_events_status
    ON events (status);

CREATE INDEX IF NOT EXISTS idx_events_kind
    ON events (kind);

CREATE INDEX IF NOT EXISTS idx_events_station
    ON events (station);

CREATE INDEX IF NOT EXISTS idx_events_code
    ON events (code);

CREATE INDEX IF NOT EXISTS idx_events_shift
    ON events (shift);

CREATE INDEX IF NOT EXISTS idx_events_closed_at
    ON events (closed_at);

CREATE INDEX IF NOT EXISTS idx_events_open_station
    ON events (station, ts DESC)
    WHERE status = 'OPEN';

CREATE INDEX IF NOT EXISTS idx_events_open_code
    ON events (code, ts DESC)
    WHERE status = 'OPEN';
"""


def get_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Restituisce connessione PostgreSQL se DATABASE_URL è configurato.
    """
    if not settings.database_configured:
        return None

    try:
        conn = psycopg2.connect(settings.database_url)
        return conn
    except Exception as e:
        print("DB connection error:", e)
        return None


def db_ping() -> bool:
    """
    Verifica se il database risponde.
    """
    conn = get_connection()

    if conn is None:
        return False

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False


def ensure_schema():
    """
    Crea schema base se non esiste.
    """
    conn = get_connection()

    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute(DEFAULT_CREATE_EVENTS_TABLE_SQL)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Schema creation error:", e)
