from __future__ import annotations

from typing import Any


VALID_CONFIDENCE = {"CERTO", "INFERITO", "DA_VERIFICARE", "TL_CONFIRMED", "TL_DA_DOCUMENTARE"}


def normalize_assembly_progression(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Normalizza la progressione assemblaggio già presente in un profilo articolo.

    Contratto:
    - non inventa stati mancanti
    - non promuove confidence
    - accetta solo lista di dict
    - conserva solo campi dominio ammessi
    """
    raw = profile.get("assembly_progression")
    if not isinstance(raw, list):
        return []

    normalized: list[dict[str, Any]] = []

    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            continue

        state = str(item.get("state") or f"STATE_{idx}").strip()
        description = str(item.get("description") or "").strip()
        confidence = str(item.get("confidence") or "DA_VERIFICARE").strip().upper()

        if confidence not in VALID_CONFIDENCE:
            confidence = "DA_VERIFICARE"

        stations = item.get("stations") if isinstance(item.get("stations"), list) else []
        related_articles = item.get("related_articles") if isinstance(item.get("related_articles"), list) else []
        components = item.get("components") if isinstance(item.get("components"), list) else []

        normalized.append(
            {
                "state": state,
                "description": description,
                "stations": [str(x).strip() for x in stations if str(x).strip()],
                "related_articles": [str(x).strip() for x in related_articles if str(x).strip()],
                "components": [str(x).strip() for x in components if str(x).strip()],
                "confidence": confidence,
                "source": str(item.get("source") or "").strip(),
            }
        )

    return normalized


def summarize_assembly_progression(profile: dict[str, Any]) -> list[str]:
    """
    Produce righe sintetiche leggibili dalla TL chat senza esporre dettagli eccessivi.
    """
    lines: list[str] = []

    for item in normalize_assembly_progression(profile):
        parts: list[str] = []

        if item["stations"]:
            parts.append("stazioni " + "+".join(item["stations"]))

        if item["related_articles"]:
            parts.append("con " + "+".join(item["related_articles"]))

        if item["components"]:
            parts.append("componenti " + "+".join(item["components"]))

        if not parts:
            continue

        lines.append(f'{item["state"]}: ' + ", ".join(parts) + f' ({item["confidence"]})')

    return lines
