from __future__ import annotations

from typing import Any

from app.domain.article_process_matrix import (
    get_article_profile,
    get_article_route,
    get_article_signals,
)


def _as_bool(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes", "sì", "si"}


def build_article_tl_summary(article_code: str) -> dict[str, Any]:
    """
    Build a Team Leader readable operational summary for one article.

    Contract:
    - read-only
    - no planner mutation
    - no SMF/database write
    - uses article_process_matrix as source
    """
    profile = get_article_profile(article_code)

    if not profile:
        return {
            "ok": False,
            "article": article_code,
            "confidence": "DA_VERIFICARE",
            "summary": f"Articolo {article_code}: profilo operativo non disponibile.",
            "route": [],
            "criticalities": ["Profilo articolo non presente in article_route_matrix."],
            "tl_action": "Verificare specifica, BOM e route prima di pianificare.",
        }

    route = get_article_route(article_code)
    signals = get_article_signals(article_code)
    discrepancies = profile.get("discrepancies") or []

    criticalities: list[str] = []

    primary_zaw = signals.get("primary_zaw_station")
    if primary_zaw:
        criticalities.append(f"Postazione ZAW primaria confermata: {primary_zaw}.")

    if _as_bool(signals.get("has_zaw1")) and not _as_bool(signals.get("has_zaw2")):
        criticalities.append("Usare ZAW1; non trattare ZAW2 come alternativa automatica.")

    if _as_bool(signals.get("has_henn")):
        criticalities.append("HENN presente: rispettare sequenza HENN prima di innesto rapido/ZAW.")

    if _as_bool(signals.get("has_pidmill")):
        criticalities.append("PIDMILL presente: verificare disponibilità attrezzaggio e componenti dedicati.")

    if _as_bool(signals.get("cp_required")):
        cp_mode = signals.get("cp_machine_mode")
        if cp_mode:
            criticalities.append(f"CP finale obbligatorio con modalità macchina {cp_mode}.")
        else:
            criticalities.append("CP finale obbligatorio.")

    if _as_bool(signals.get("shared_component_risk")):
        shared = signals.get("shared_components") or []
        if shared:
            criticalities.append(
                "Componenti condivisi da monitorare: " + ", ".join(str(x) for x in shared) + "."
            )
        else:
            criticalities.append("Rischio componenti condivisi da verificare.")

    if _as_bool(signals.get("long_sheath_risk")):
        criticalities.append("Guaina lunga: possibile impatto su manipolazione e sequenza operativa.")

    for item in discrepancies:
        if not isinstance(item, dict):
            continue
        code = item.get("code", "discrepancy")
        status = item.get("status", "DA_VERIFICARE")
        correct = item.get("correct_value")
        if correct:
            criticalities.append(f"Discrepanza {code}: valore corretto {correct}, stato {status}.")
        else:
            criticalities.append(f"Discrepanza {code}: stato {status}.")

    if not criticalities:
        criticalities.append("Nessuna criticità specifica registrata nel profilo articolo.")

    route_text = " → ".join(route) if route else "route non disponibile"
    confidence = str(profile.get("confidence") or "DA_VERIFICARE")

    tl_action = "Seguire route confermata e usare criticità come checklist TL."
    if discrepancies:
        tl_action = "Seguire route confermata; non usare fonti discordanti senza verifica TL."

    return {
        "ok": True,
        "article": str(profile.get("article") or article_code),
        "confidence": confidence,
        "route": route,
        "signals": signals,
        "criticalities": criticalities,
        "tl_action": tl_action,
        "summary": f"Articolo {article_code} — profilo operativo {confidence}. Route: {route_text}.",
    }
