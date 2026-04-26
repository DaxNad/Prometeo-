from typing import Dict, List
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def _split_components(raw):
    if not raw:
        return []
    return [c.strip() for c in str(raw).split("|") if c.strip()]


def build_component_usage_from_db(db: Session) -> Dict[str, int]:
    """
    Conta componenti su ORDINI ATTIVI (no completati).
    Fonte: viste ZAW → già filtrate operativamente.
    """
    usage: Dict[str, int] = {}

    queries = [
        "SELECT componenti_condivisi FROM vw_tl_zaw1_board",
        "SELECT componenti_condivisi FROM vw_tl_zaw2_board",
    ]

    registry_query = """
        SELECT codice_componente
        FROM component_usage_registry
        WHERE condiviso IS TRUE
          AND codice_componente IS NOT NULL
    """

    if db is None:
        return usage

    for q in queries:
        try:
            rows = db.execute(text(q)).fetchall()
        except SQLAlchemyError:
            # Test SQLite / ambienti senza viste TL: fallback neutro.
            continue

        for r in rows:
            components = _split_components(r[0])

            for c in components:
                usage[c] = usage.get(c, 0) + 1

    try:
        registry_rows = db.execute(text(registry_query)).fetchall()
    except SQLAlchemyError:
        registry_rows = []

    for r in registry_rows:
        component = str(r[0] or "").strip()
        if component:
            usage[component] = usage.get(component, 0) + 1

    return usage


def apply_component_impact(items: List[dict], usage: Dict[str, int]) -> List[dict]:
    for item in items:
        impact = False
        impact_reasons: list[str] = []

        for c in item.get("shared_components", []):
            count = usage.get(c, 0)
            if count > 1:
                impact = True
                impact_reasons.append(
                    f"{c} shared across {count} articoli"
                )

        item["shared_component_impact"] = impact
        item["shared_component_impact_reason"] = "; ".join(impact_reasons)

    return items


def get_component_conflicts(components):
    """
    Versione temporanea (compatibilità atlas_merge)
    """
    usage = {}
    for c in components or []:
        if not c:
            continue
        usage[c] = usage.get(c, 0) + 1

    level = "LOW"
    score = 0.2

    if any(v > 2 for v in usage.values()):
        level = "HIGH"
        score = 0.9
    elif any(v > 1 for v in usage.values()):
        level = "MEDIUM"
        score = 0.6

    return {
        "level": level,
        "score": score,
        "details": usage
    }
