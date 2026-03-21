from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = Path(
    os.getenv(
        "PROMETEO_DATA_DIR",
        BASE_DIR / "data"
    )
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "prometeo.sqlite3"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
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
