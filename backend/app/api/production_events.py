from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db.session import get_db


def _serialize_created_at(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)

router = APIRouter(prefix="/production", tags=["production-events"])


@router.get("/events")
def production_events(db: Session = Depends(get_db)):
    """Read-only audit stream for production_events.

    This endpoint is not the same contract as /events/*.
    /production/events reads the immutable production audit table.
    /events/* handles secondary operational station signals.
    """
    try:
        rows = db.execute(
            text(
                """
                SELECT id, order_id, event_type, payload, created_at
                FROM production_events
                ORDER BY created_at DESC
                LIMIT 200
                """
            )
        ).mappings().all()

        return {
            "ok": True,
            "event_store": "production_events",
            "contract": "production_audit_readonly",
            "count": len(rows),
            "items": [
                {
                    "id": r["id"],
                    "order_id": r["order_id"],
                    "event_type": r["event_type"],
                    "payload": r["payload"],
                    "created_at": _serialize_created_at(r["created_at"]),
                }
                for r in rows
            ],
        }
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "event_store": "production_events",
                "contract": "production_audit_readonly",
                "count": 0,
                "items": [],
                "error_code": "PRODUCTION_EVENTS_UNAVAILABLE",
                "detail": f"{exc.__class__.__name__}: {exc}",
            },
        )
