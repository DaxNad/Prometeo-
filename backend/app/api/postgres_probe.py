from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..config import settings
from ..db import probe_postgres
from ..repositories.postgres_events_repository import PostgresEventsRepository

router = APIRouter(tags=["Postgres Probe"])

repo = PostgresEventsRepository()


@router.get("/db/ping")
def db_ping():
    result = probe_postgres()

    if not result["configured"]:
        raise HTTPException(status_code=400, detail="DATABASE_URL non configurato")

    if not result["reachable"]:
        raise HTTPException(status_code=503, detail=result["message"])

    return {
        "ok": True,
        "backend": "postgres",
        "message": result["message"],
        "result": result.get("result"),
    }


@router.get("/postgres/ping")
def postgres_ping():
    return db_ping()


@router.post("/postgres/init")
def postgres_init():
    if not settings.postgres_configured:
        raise HTTPException(status_code=400, detail="DATABASE_URL non configurato")

    repo.ensure_schema()
    return {
        "ok": True,
        "message": "Schema PostgreSQL inizializzato",
    }


@router.get("/postgres/events")
def postgres_events():
    if not settings.postgres_configured:
        raise HTTPException(status_code=400, detail="DATABASE_URL non configurato")

    return {
        "ok": True,
        "items": repo.list_events(),
    }
