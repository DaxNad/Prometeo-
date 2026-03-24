from pathlib import Path

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

router = APIRouter()

SQL_FILE = Path("backend/sql/003_bom_registry.sql")


@router.post("/dev/init-bom-db")
def init_bom_db():
    if not SQL_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=f"SQL file non trovato: {SQL_FILE}",
        )

    from app.db.session import engine

    sql = SQL_FILE.read_text(encoding="utf-8")

    with engine.begin() as conn:
        conn.execute(text(sql))

    return {
        "status": "ok",
        "tables_created": [
            "bom_specs",
            "bom_components",
            "bom_operations",
            "bom_markings",
            "bom_controls",
            "bom_variants",
        ],
    }
