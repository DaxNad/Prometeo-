from __future__ import annotations

from .events_repository import EventsRepository
from .postgres_events_repository import PostgresEventsRepository
from .sqlite_events_repository import SQLiteEventsRepository
from ..config import settings


def get_events_repository() -> EventsRepository:
    if settings.db_backend == "postgres":
        return PostgresEventsRepository()
    return SQLiteEventsRepository()
