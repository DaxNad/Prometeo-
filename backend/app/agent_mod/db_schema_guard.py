from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text


REQUIRED_TABLES: List[str] = [
    "production_orders",
    "production_events",
    "customer_demand",
    "component_usage_registry",
    "agent_runs",
]

REQUIRED_VIEWS: List[str] = [
    "vw_zaw_group_load",
    "vw_zaw1_sequence_ranked",
    "vw_machine_load_summary",
    "vw_tl_zaw1_board",
    "vw_tl_pidmill_board",
    "vw_componenti_condivisi_critici",
]


def _load_engine():
    # Importa l'engine SQLAlchemy già configurato dal backend
    from app.db.session import engine

    return engine


def _detect_backend() -> Tuple[str, bool, Optional[str]]:
    env_url = os.getenv("DATABASE_URL", "").strip()
    if not env_url:
        return "unknown", False, "DATABASE_URL not set"

    url = env_url.lower()
    is_pg = url.startswith("postgresql://") or url.startswith("postgresql+") or url.startswith("postgres://")
    if not is_pg:
        return "non_postgres", False, "DATABASE_URL is not PostgreSQL"

    try:
        engine = _load_engine()
        dialect = getattr(engine.dialect, "name", "unknown")
        if dialect != "postgresql":
            return dialect, False, f"Engine dialect is '{dialect}', expected 'postgresql'"
        return "postgres", True, None
    except Exception as exc:
        return "unknown", False, f"engine load error: {exc}"


def _fetch_table_names(engine) -> List[str]:
    sql = text(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()
    return [str(r[0]).lower() for r in rows]


def _fetch_view_names(engine) -> List[str]:
    sql = text(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()
    return [str(r[0]).lower() for r in rows]


def run_db_schema_guard() -> Dict[str, Any]:
    backend, usable, reason = _detect_backend()

    result: Dict[str, Any] = {
        "db_schema_guard": "FAIL",
        "backend": backend,
        "checks": {
            "tables": False,
            "views": False,
        },
        "missing_tables": [],
        "missing_views": [],
    }

    if not usable:
        if reason:
            result["reason"] = reason
        return result

    try:
        engine = _load_engine()
        existing_tables = set(_fetch_table_names(engine))
        existing_views = set(_fetch_view_names(engine))

        missing_tables = [t for t in REQUIRED_TABLES if t.lower() not in existing_tables]
        missing_views = [v for v in REQUIRED_VIEWS if v.lower() not in existing_views]

        result["missing_tables"] = missing_tables
        result["missing_views"] = missing_views
        result["checks"]["tables"] = len(missing_tables) == 0
        result["checks"]["views"] = len(missing_views) == 0

        if result["checks"]["tables"] and result["checks"]["views"]:
            result["db_schema_guard"] = "PASS"
        else:
            result["db_schema_guard"] = "FAIL"
        return result
    except Exception as exc:
        result["reason"] = f"introspection error: {exc}"
        return result


def main() -> None:
    data = run_db_schema_guard()
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0 if data.get("db_schema_guard") == "PASS" else 1)


if __name__ == "__main__":
    main()
