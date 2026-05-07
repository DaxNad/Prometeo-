from __future__ import annotations

from typing import Any

VALID_OPERATIONAL_CLASSES = {
    "STANDARD",
    "RICAMBIO",
    "ONE_SHOT",
    "REFERENCE_ONLY",
    "DA_VERIFICARE",
}

NON_STANDARD_CLASSES = {
    "RICAMBIO",
    "ONE_SHOT",
    "REFERENCE_ONLY",
    "DA_VERIFICARE",
}


def _as_bool(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes", "sì", "si"}


def normalize_operational_class(value: Any) -> str:
    raw = str(value or "").strip().upper().replace("-", "_").replace(" ", "_")

    aliases = {
        "SPARE": "RICAMBIO",
        "SPARE_PART": "RICAMBIO",
        "RICAMBI": "RICAMBIO",
        "ONE_SHOT_SPARE": "ONE_SHOT",
        "ONE_SHOT_SPARE_PART": "ONE_SHOT",
        "REFERENCE": "REFERENCE_ONLY",
        "SOLO_RIFERIMENTO": "REFERENCE_ONLY",
        "DA_VERIFICARE": "DA_VERIFICARE",
        "TO_VERIFY": "DA_VERIFICARE",
        "UNKNOWN": "DA_VERIFICARE",
        "": "DA_VERIFICARE",
    }

    normalized = aliases.get(raw, raw)

    if normalized in VALID_OPERATIONAL_CLASSES:
        return normalized

    return "DA_VERIFICARE"


def build_operational_policy(profile: dict[str, Any] | None) -> dict[str, Any]:
    """
    PROMETEO domain rule:
    - PROMETEO must know more codes than it automatically plans.
    - STANDARD can enter ordinary planning.
    - Active customer order can make a non-standard code planner-visible.
    - RICAMBIO / ONE_SHOT / REFERENCE_ONLY remain non-standard.
    - DA_VERIFICARE never enters automatic planning.
    """
    profile = profile or {}

    operational_class = normalize_operational_class(
        profile.get("operational_class")
        or profile.get("classe_operativa")
        or profile.get("planning_class")
        or profile.get("categoria_operativa")
    )

    active_customer_order = _as_bool(
        profile.get("active_customer_order")
        or profile.get("ordine_cliente_attivo")
        or profile.get("customer_order_active")
    )

    planner_eligible = False
    if operational_class == "STANDARD":
        planner_eligible = True
    elif active_customer_order and operational_class != "DA_VERIFICARE":
        planner_eligible = True

    tl_confirmation_required = operational_class != "STANDARD"

    return {
        "operational_class": operational_class,
        "active_customer_order": active_customer_order,
        "planner_eligible": planner_eligible,
        "tl_confirmation_required": tl_confirmation_required,
        "planner_rule": (
            "STANDARD_OR_ACTIVE_CUSTOMER_ORDER"
            if planner_eligible
            else "REFERENCE_ONLY_UNTIL_ORDER_OR_TL_CONFIRMATION"
        ),
    }
