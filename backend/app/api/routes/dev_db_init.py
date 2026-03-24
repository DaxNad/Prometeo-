from fastapi import APIRouter
from sqlalchemy import text
from pathlib import Path
from app.db.session import engine

router = APIRouter()

SQL_FILE = Path("backend/sql/003_bom_registry.sql")

@router.post("/dev/init-bom-db")
def init_bom_db():

    sql = SQL_FILE.read_text()

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
            "bom_variants"
        ]
    }
