from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db.session import get_db

router = APIRouter(prefix="/production", tags=["production"])


@router.get("/events")
def production_events(db: Session = Depends(get_db)):
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
            "count": len(rows),
            "items": [
                {
                    "id": r["id"],
                    "order_id": r["order_id"],
                    "event_type": r["event_type"],
                    "payload": r["payload"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                }
                for r in rows
            ],
        }
    except Exception as exc:
        return {
            "ok": True,
            "count": 0,
            "items": [],
            "warning": f"production_events non disponibile: {exc.__class__.__name__}: {exc}",
        }
