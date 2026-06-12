#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


ALLOWED_VERDICTS = {"CERTO", "INFERITO", "DA_VERIFICARE"}
ALLOWED_RISKS = {"LOW", "MEDIUM", "HIGH"}

RISK_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


@dataclass
class ValidationResult:
    verdict: str
    risk: str
    summary: str
    suggested_next_command: None
    requires_human_confirmation: bool
    corrections: list[str]


def extract_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        text = text[start:end + 1]

    return json.loads(text)


def min_risk(current: str, minimum: str) -> str:
    if current not in RISK_ORDER:
        return minimum
    return current if RISK_ORDER[current] >= RISK_ORDER[minimum] else minimum


def norm(text: str) -> str:
    return text.lower()


def has_tl_confirmation_zaw1(text: str) -> bool:
    t = norm(text)
    return (
        "conferma tl" in t
        and "zaw1" in t
        and ("non zaw2" in t or "non è zaw2" in t or "non e zaw2" in t)
    )


def has_tl_contradiction(text: str) -> bool:
    t = norm(text)
    return (
        "conferma tl" in t
        and "zaw1" in t
        and "zaw2" in t
        and ("forse" in t or "contraddittorie" in t or "contraddizione" in t)
    )


def has_derived_zaw2_without_tl(text: str) -> bool:
    t = norm(text)
    derived_source = (
        "bom" in t
        or "famiglia_processo" in t
        or "famiglia processo" in t
        or "cache" in t
        or "preview" in t
        or "fonte derivata" in t
    )
    no_tl = "non è presente conferma tl" in t or "non e presente conferma tl" in t or "manca la conferma tl" in t
    return derived_source and "zaw2" in t and no_tl


def cp_required_but_missing(text: str) -> bool:
    t = norm(text)
    cp_required = "cp finale obbligatorio" in t or "cp finale" in t or "controllo finale" in t
    missing_cp = (
        "non include cp" in t
        or "manca cp" in t
        or "mancando la postazione" in t
        or "termina a pidmill" in t
    )
    return cp_required and missing_cp


def guarded_summary(original_summary: str, corrections: list[str]) -> str:
    if not corrections:
        return original_summary.strip()

    if "TL_CONTRADICTION_FORCED_DA_VERIFICARE" in corrections:
        return (
            "DA_VERIFICARE: sono presenti indicazioni TL contraddittorie. "
            "Serve nuova conferma operativa prima di classificare il caso come certo."
        )

    if (
        "DERIVED_ZAW2_WITHOUT_TL_FORCED_DA_VERIFICARE" in corrections
        or "DERIVED_ZAW2_WITHOUT_TL_MIN_RISK_MEDIUM" in corrections
    ):
        return (
            "DA_VERIFICARE: una fonte derivata propone ZAW2 senza conferma TL. "
            "ZAW2 non deve essere inferita automaticamente; rischio minimo MEDIUM."
        )

    if "CP_REQUIRED_MISSING_FORCED_DA_VERIFICARE" in corrections:
        return (
            "DA_VERIFICARE: la route fornita non include CP finale nonostante il vincolo "
            "di CP obbligatorio. Serve correzione o conferma TL."
        )

    if "TL_AUTHORITY_FORCED_CERTO" in corrections:
        return (
            "CERTO: la conferma TL esplicita prevale sulla fonte derivata e la route "
            "risulta completa con CP finale."
        )

    return original_summary.strip()


def route_complete_with_cp(text: str) -> bool:
    t = norm(text)
    return (
        "route corretta" in t
        and "henn" in t
        and "zaw1" in t
        and "pidmill" in t
        and "cp" in t
    )


def validate_domain_output(case_text: str, raw_model_output: str) -> dict[str, Any]:
    corrections: list[str] = []

    try:
        data = extract_json(raw_model_output)
    except Exception as exc:
        return ValidationResult(
            verdict="DA_VERIFICARE",
            risk="HIGH",
            summary=f"Output modello non JSON valido: {exc}",
            suggested_next_command=None,
            requires_human_confirmation=True,
            corrections=["INVALID_JSON_FAIL_CLOSED"],
        ).__dict__

    verdict = data.get("verdict")
    risk = data.get("risk")
    summary = data.get("summary")
    requires_human_confirmation = data.get("requires_human_confirmation")

    if verdict not in ALLOWED_VERDICTS:
        verdict = "DA_VERIFICARE"
        risk = "HIGH"
        requires_human_confirmation = True
        corrections.append("INVALID_VERDICT_FAIL_CLOSED")

    if risk not in ALLOWED_RISKS:
        risk = "HIGH"
        requires_human_confirmation = True
        corrections.append("INVALID_RISK_FAIL_CLOSED")

    if not isinstance(summary, str) or not summary.strip():
        summary = "Output modello incompleto o privo di sintesi utile."
        verdict = "DA_VERIFICARE"
        risk = "HIGH"
        requires_human_confirmation = True
        corrections.append("MISSING_SUMMARY_FAIL_CLOSED")

    if not isinstance(requires_human_confirmation, bool):
        requires_human_confirmation = True
        verdict = "DA_VERIFICARE"
        risk = min_risk(risk, "HIGH")
        corrections.append("INVALID_CONFIRMATION_FLAG_FAIL_CLOSED")

    # Rule 1: contraddizione TL interna -> blocco forte.
    if has_tl_contradiction(case_text):
        if verdict != "DA_VERIFICARE":
            corrections.append("TL_CONTRADICTION_FORCED_DA_VERIFICARE")
        verdict = "DA_VERIFICARE"
        risk = min_risk(risk, "HIGH")
        requires_human_confirmation = True

    # Rule 2: fonte derivata propone ZAW2 senza TL -> mai CERTO, rischio almeno MEDIUM.
    if has_derived_zaw2_without_tl(case_text):
        if verdict != "DA_VERIFICARE":
            corrections.append("DERIVED_ZAW2_WITHOUT_TL_FORCED_DA_VERIFICARE")
        verdict = "DA_VERIFICARE"
        risk = min_risk(risk, "MEDIUM")
        requires_human_confirmation = True
        if "DERIVED_ZAW2_WITHOUT_TL_MIN_RISK_MEDIUM" not in corrections:
            corrections.append("DERIVED_ZAW2_WITHOUT_TL_MIN_RISK_MEDIUM")

    # Rule 3: CP obbligatorio ma mancante -> DA_VERIFICARE HIGH.
    if cp_required_but_missing(case_text):
        if verdict != "DA_VERIFICARE":
            corrections.append("CP_REQUIRED_MISSING_FORCED_DA_VERIFICARE")
        verdict = "DA_VERIFICARE"
        risk = min_risk(risk, "HIGH")
        requires_human_confirmation = True

    # Rule 4: TL esplicito ZAW1 batte BOM, se non ci sono contraddizioni e la route è completa.
    if (
        has_tl_confirmation_zaw1(case_text)
        and not has_tl_contradiction(case_text)
        and not cp_required_but_missing(case_text)
        and route_complete_with_cp(case_text)
    ):
        if verdict != "CERTO":
            corrections.append("TL_AUTHORITY_FORCED_CERTO")
        if requires_human_confirmation is not False:
            corrections.append("TL_ALREADY_CONFIRMED_FORCED_NO_CONFIRMATION")
        verdict = "CERTO"
        requires_human_confirmation = False

    final_summary = guarded_summary(summary, corrections)

    return ValidationResult(
        verdict=verdict,
        risk=risk,
        summary=final_summary,
        suggested_next_command=None,
        requires_human_confirmation=requires_human_confirmation,
        corrections=corrections,
    ).__dict__
