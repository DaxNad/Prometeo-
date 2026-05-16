from __future__ import annotations

from typing import Any

from app.semantic_registry import get_semantic_gate_entry

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


def _resolve_planner_admission_gate_metadata() -> dict[str, Any]:
    """
    Read-only semantic bridge for planner admission.

    Existing boolean admission logic remains local and unchanged; this metadata
    records the canonical gate authority for diagnostics and future resolver use.
    """
    gate = get_semantic_gate_entry("PLANNER_ADMISSION_GATE")
    return {
        "key": gate.key,
        "authority": gate.authority,
        "master_refs": gate.master_refs,
        "inputs": gate.inputs,
        "pass_rule": gate.pass_rule,
        "fail_rule": gate.fail_rule,
    }


def build_planner_admission_gate(profile: dict[str, Any] | None) -> dict[str, Any]:
    """
    PROMETEO planner gate.

    planner_eligible=true does not mean automatic production priority.
    It only means the article can be considered by the planner if runtime
    admission prerequisites are also satisfied.
    """
    profile = profile or {}
    policy = build_operational_policy(profile)
    semantic_gate = _resolve_planner_admission_gate_metadata()

    operational_class = policy["operational_class"]
    planner_eligible = bool(policy["planner_eligible"])
    route_status = str(profile.get("route_status") or "").strip().upper()
    confidence = str(profile.get("confidence") or "").strip().upper()

    has_active_demand = _as_bool(
        profile.get("active_customer_order")
        or profile.get("ordine_cliente_attivo")
        or profile.get("customer_order_active")
        or profile.get("active_lot")
        or profile.get("lotto_attivo")
        or profile.get("explicit_operational_request")
        or profile.get("richiesta_operativa_esplicita")
    )

    has_blocking_constraint = _as_bool(
        profile.get("has_blocking_constraint")
        or profile.get("vincolo_bloccante_aperto")
        or profile.get("open_blocking_constraint")
    )

    reasons: list[str] = []

    if operational_class != "STANDARD":
        reasons.append("operational_class_not_standard")

    if not planner_eligible:
        reasons.append("planner_eligible_false")

    if route_status != "CERTO":
        reasons.append("route_status_not_certo")

    if confidence != "CERTO":
        reasons.append("confidence_not_certo")

    if has_blocking_constraint:
        reasons.append("blocking_constraint_open")

    if not has_active_demand:
        reasons.append("no_active_customer_order_lot_or_explicit_request")

    admitted = not reasons

    return {
        "planner_admitted": admitted,
        "planner_eligible": planner_eligible,
        "operational_class": operational_class,
        "route_status": route_status or "DA_VERIFICARE",
        "confidence": confidence or "DA_VERIFICARE",
        "has_active_demand": has_active_demand,
        "has_blocking_constraint": has_blocking_constraint,
        "human_override_allowed": True,
        "reasons": reasons,
        "rule": "STANDARD_CERTAIN_ROUTE_CERTAIN_CONFIDENCE_NO_BLOCKERS_ACTIVE_DEMAND_HUMAN_OVERRIDE",
        "semantic_gate": semantic_gate,
    }
