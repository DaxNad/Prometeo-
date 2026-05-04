
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

    route = payload.get("route") or []

    smf_row_preview = {
        "id": payload.get("order_id"),
        "codice_articolo": payload.get("codice"),
        "quantita": payload.get("qta"),
        "cliente": payload.get("cliente"),
        "data_scadenza": payload.get("due_date"),
        "postazione_principale": route[0] if route else None,
        "route": route,
        "stato": "DA_VALIDARE",
        "origine": "REAL_INGEST_PREVIEW",
    }

    validation = {
        "is_valid": True,
        "missing_fields": missing,
        "warnings": [],
        "blocking_errors": [],
    }

    if not route:
        validation["is_valid"] = False
        validation["blocking_errors"].append("route_empty")

    if route and route[-1] != "CP":
        validation["warnings"].append("route_without_final_CP")

    return {
        "ok": validation["is_valid"],
        "validated": True,
        "smf_row_preview": smf_row_preview,
        "validation": validation,
        "note": "Preview SMFRow — nessuna scrittura su SMF/database"
    }
