from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["default"])

SQL_DIR = Path(__file__).resolve().parents[3] / "sql"

SQL_FILES = [
    "003_bom_registry.sql",
    "004_bom_variants_extension.sql",
    "004_complessivi_registry.sql",
    "004_view_complessivi.sql",
    "004b_bom_variants_alter.sql",
    "005_tl_variant_alert_view.sql",
    "006_component_usage_registry.sql",
    "006_view_componenti_critici.sql",
    "007_customer_demand_registry.sql",
    "007_view_zaw1_component_load.sql",
    "007_view_zaw1_sequence.sql",
    "007_view_zaw1_sequence_ranked.sql",
    "007_view_zaw1_sequence_tl.sql",
    "008_view_tl_zaw1_board.sql",
]


@router.post("/dev/init-bom-db")
def init_bom_db(db: Session = Depends(get_db)):
    executed = []
    missing = []

    for filename in SQL_FILES:
        sql_file = SQL_DIR / filename

        if not sql_file.exists():
            missing.append(str(sql_file))
            continue

        try:
            sql_text = sql_file.read_text(encoding="utf-8")
            db.execute(text(sql_text))
            db.commit()
            executed.append(filename)
        except Exception as exc:
            db.rollback()
            return {
                "ok": False,
                "sql_dir": str(SQL_DIR),
                "executed_files": executed,
                "missing_files": missing,
                "failed_file": filename,
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            }

    return {
        "ok": len(missing) == 0,
        "sql_dir": str(SQL_DIR),
        "executed_files": executed,
        "missing_files": missing,
    }
