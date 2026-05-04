
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

@router.post("/real/ingest-order")
def ingest_real_order(payload: dict, db: Session = Depends(get_db)):
    """
    Ingest controllato articoli reali
    NON scrive direttamente in produzione
    """
    required = ["order_id", "codice", "qta", "route"]

    missing = [k for k in required if k not in payload]
    if missing:
        return {"ok": False, "error": f"missing_fields: {missing}"}

    return {
        "ok": True,
        "validated": True,
        "order_preview": {
            "order_id": payload.get("order_id"),
            "codice": payload.get("codice"),
            "qta": payload.get("qta"),
            "route": payload.get("route"),
        },
        "note": "Non inserito in produzione — solo validazione"
    }
