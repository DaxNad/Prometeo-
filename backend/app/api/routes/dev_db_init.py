from pathlib import Path

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()

SQL_FILES = [
    # --- BOM / REGISTRI BASE ---
    "003_bom_registry.sql",
    "004b_bom_variants_alter.sql",
    "004_bom_variants_extension.sql",
    "004_complessivi_registry.sql",
    "004_view_complessivi.sql",
    "005_tl_variant_alert_view.sql",
    # --- COMPONENTI / CRITICITÀ ---
    "006_component_usage_registry.sql",
    "006_view_componenti_critici.sql",
    # --- DOMANDA CLIENTE ---
    "007_customer_demand_registry.sql",
    # --- ZAW OFFICIAL CHAIN ---
    "007_view_zaw1_component_load.sql",
    "007_view_zaw1_sequence_ranked.sql",
    "008_view_tl_zaw1_board.sql",
    "007_view_zaw2_component_load.sql",
    "007_view_zaw2_sequence_ranked.sql",
    "008_view_tl_zaw2_board.sql",
    # --- MACHINE LOAD ---
    "010_machine_load_summary.sql",
]

BASE_SQL_PATH = Path(__file__).resolve().parents[3] / "sql"

RESET_VIEWS_SQL = """
DROP VIEW IF EXISTS vw_tl_zaw1_board CASCADE;
DROP VIEW IF EXISTS vw_tl_zaw2_board CASCADE;
DROP VIEW IF EXISTS vw_zaw1_tl_board CASCADE;
DROP VIEW IF EXISTS vw_zaw1_sequence_ranked CASCADE;
DROP VIEW IF EXISTS vw_zaw2_sequence_ranked CASCADE;
DROP VIEW IF EXISTS vw_zaw1_sequence_ranked_constrained CASCADE;
DROP VIEW IF EXISTS vw_zaw1_sequence_with_constraints CASCADE;
DROP VIEW IF EXISTS vw_zaw1_sequence_suggestions CASCADE;
DROP VIEW IF EXISTS vw_zaw1_sequence_tl CASCADE;
DROP VIEW IF EXISTS vw_machine_load_summary CASCADE;
"""


@router.post("/dev/init-bom-db")
def init_bom_db():
    executed = []

    try:
        with engine.begin() as conn:
            conn.execute(text(RESET_VIEWS_SQL))
            executed.append("__RESET_VIEWS__")

            for filename in SQL_FILES:
                path = BASE_SQL_PATH / filename

                if not path.exists():
                    raise HTTPException(
                        status_code=500,
                        detail=f"SQL file missing: {filename}",
                    )

                sql = path.read_text(encoding="utf-8")
                conn.execute(text(sql))
                executed.append(filename)

        return {
            "ok": True,
            "message": "Bootstrap SQL completed",
            "sql_path": str(BASE_SQL_PATH),
            "executed_count": len(executed),
            "executed": executed,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "message": "Bootstrap SQL failed",
                "error": str(e),
                "executed_before_error": executed,
            },
        )
