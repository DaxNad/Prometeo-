from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db import get_db

router = APIRouter(tags=["default"])

SQL_DIR = Path(__file__).resolve().parents[3] / "sql"

SQL_FILES = [
    "003_bom_registry.sql",
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

        sql_text = sql_file.read_text(encoding="utf-8")
        db.execute(text(sql_text))
        executed.append(filename)

    db.commit()

    return {
        "ok": len(missing) == 0,
        "sql_dir": str(SQL_DIR),
        "executed_files": executed,
        "missing_files": missing,
    }
