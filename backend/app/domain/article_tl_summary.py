from __future__ import annotations

from typing import Any

from app.domain.article_operational_registry import get_operational_registry_entry
from app.domain.operational_class import build_operational_policy
from app.domain.article_profile_resolver import resolve_article_profile


def _as_bool(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes", "sì", "si"}


def build_article_tl_summary(article_code: str) -> dict[str, Any]:
    """
    Build a Team Leader readable operational summary for one article.

    Contract:
    - read-only
    - no planner mutation
    - no SMF/database write
    - uses authoritative article profile resolver
    """
    profile = resolve_article_profile(article_code)

    if not profile:
        registry_entry = get_operational_registry_entry(article_code)
        operational_policy = build_operational_policy(registry_entry)

        if registry_entry:
            drawing = registry_entry.get("drawing") or "disegno non disponibile"
            description = registry_entry.get("description") or "descrizione non disponibile"
            return {
                "ok": True,
                "article": str(registry_entry.get("article") or article_code),
                "confidence": "CERTO",
                "operational_class": operational_policy["operational_class"],
                "planner_eligible": operational_policy["planner_eligible"],
                "tl_confirmation_required": operational_policy["tl_confirmation_required"],
                "operational_policy": operational_policy,
                "route": [],
                "signals": {},
                "criticalities": [
                    f"Codice noto da registro operativo: {description}.",
                    f"Disegno associato: {drawing}.",
                    f"Classe operativa {operational_policy['operational_class']}: non entra nel planner standard senza ordine esplicito o conferma TL.",
                ],
                "tl_action": "Usare come riferimento/ricambio/one-shot; non pianificare automaticamente senza ordine esplicito o conferma TL.",
                "summary": (
                    f"Articolo {article_code} — noto in registro operativo "
                    f"come {operational_policy['operational_class']}. "
                    "Route produttiva non strutturata."
                ),
            }

        operational_policy = build_operational_policy(None)
        return {
            "ok": False,
            "article": article_code,
            "confidence": "DA_VERIFICARE",
            "operational_class": operational_policy["operational_class"],
            "planner_eligible": operational_policy["planner_eligible"],
            "tl_confirmation_required": operational_policy["tl_confirmation_required"],
            "operational_policy": operational_policy,
            "summary": f"Articolo {article_code}: profilo operativo non disponibile.",
            "route": [],
            "criticalities": ["Profilo articolo non presente in article_route_matrix."],
            "tl_action": "Verificare specifica, BOM e route prima di pianificare.",
        }

    route = profile.get("route") if isinstance(profile.get("route"), list) else []
    signals = profile.get("signals") if isinstance(profile.get("signals"), dict) else {}
    discrepancies = profile.get("discrepancies") or []
    registry_entry = get_operational_registry_entry(article_code)
    policy_source = {**(registry_entry or {}), **profile}
    operational_policy = build_operational_policy(policy_source)

    criticalities: list[str] = []

    if not operational_policy["planner_eligible"]:
        criticalities.append(
            f"Classe operativa {operational_policy['operational_class']}: "
            "non entra nel planner standard senza ordine esplicito o conferma TL."
        )

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
        "operational_class": operational_policy["operational_class"],
        "planner_eligible": operational_policy["planner_eligible"],
        "tl_confirmation_required": operational_policy["tl_confirmation_required"],
        "operational_policy": operational_policy,
        "route": route,
        "signals": signals,
        "criticalities": criticalities,
        "tl_action": tl_action,
        "summary": f"Articolo {article_code} — profilo operativo {confidence}. Route: {route_text}.",
    }
