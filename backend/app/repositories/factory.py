from __future__ import annotations

from .events_repository import EventsRepository
from .postgres_events_repository import PostgresEventsRepository
from .sqlite_events_repository import SQLiteEventsRepository
from ..config import settings


def get_events_repository() -> EventsRepository:
    """Return repository backend.

    PostgreSQL is the central domain authority when configured;
    SQLite is edge cache/staging/offline fallback only.
    """
    if settings.db_backend == "postgres":
        return PostgresEventsRepository()
    return SQLiteEventsRepository()
