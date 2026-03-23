from fastapi import APIRouter
from sqlalchemy import text

from ..config import settings
from ..db import current_backend, probe_postgres
from ..db.session import SessionLocal

router = APIRouter(prefix="/devos", tags=["DEV OS"])


@router.get("/status")
def devos_status():
    postgres_probe = probe_postgres()

    board_count = 0
    events_count = 0

    try:
        with SessionLocal() as db:
            try:
                row = db.execute(
                    text("SELECT COUNT(*) AS total FROM board_state")
                ).mappings().first()
                board_count = int(row["total"]) if row else 0
            except Exception:
                board_count = 0

            try:
                row = db.execute(
                    text("SELECT COUNT(*) AS total FROM production_events")
                ).mappings().first()
                events_count = int(row["total"]) if row else 0
            except Exception:
                events_count = 0
    except Exception:
        pass

    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.version,
        "runtime": {
            "db_backend": current_backend(),
            "postgres": {
                "configured": settings.postgres_configured,
                "reachable": postgres_probe["reachable"],
                "message": postgres_probe["message"],
            },
        },
        "resources": {
            "board_items": board_count,
            "events_items": events_count,
        },
        "ui_available": settings.ui_available,
    }
