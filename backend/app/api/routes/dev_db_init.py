from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

SQL_FILE = Path(__file__).resolve().parents[3] / "sql" / "003_bom_registry.sql"


@router.post("/dev/init-bom-db")
def init_bom_db():
    if not SQL_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=f"SQL file non trovato: {SQL_FILE}",
        )

    from ...db.session import engine

    sql = SQL_FILE.read_text(encoding="utf-8").strip()

    if not sql:
        raise HTTPException(
            status_code=400,
            detail="SQL file vuoto",
        )

    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        cursor.execute(sql)
        raw_conn.commit()
        cursor.close()
    except Exception as e:
        raw_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore init BOM DB: {e}",
        )
    finally:
        raw_conn.close()

    return {
        "status": "ok",
        "sql_file": str(SQL_FILE),
        "tables_created": [
            "bom_specs",
            "bom_components",
            "bom_operations",
            "bom_markings",
            "bom_controls",
            "bom_variants",
        ],
    }
