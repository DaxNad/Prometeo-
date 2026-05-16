from app.domain.operational_class import (
    _resolve_planner_admission_gate_metadata,
    build_operational_policy,
    build_planner_admission_gate,
    normalize_operational_class,
)


def test_standard_code_is_planner_eligible():
    policy = build_operational_policy({"operational_class": "STANDARD"})

    assert policy["operational_class"] == "STANDARD"
    assert policy["planner_eligible"] is True
    assert policy["tl_confirmation_required"] is False


def test_brown_like_reference_code_is_not_planner_eligible_by_default():
    policy = build_operational_policy({"operational_class": "REFERENCE_ONLY"})

    assert policy["operational_class"] == "REFERENCE_ONLY"
    assert policy["planner_eligible"] is False
    assert policy["tl_confirmation_required"] is True


def test_spare_part_with_active_customer_order_can_enter_planner_with_tl_control():
    policy = build_operational_policy(
        {
            "operational_class": "RICAMBIO",
            "active_customer_order": True,
        }
    )

    assert policy["operational_class"] == "RICAMBIO"
    assert policy["planner_eligible"] is True
    assert policy["tl_confirmation_required"] is True


def test_unknown_class_falls_back_to_da_verificare_and_blocks_planner():
    policy = build_operational_policy({"operational_class": "marrone_fuori_programma"})

    assert policy["operational_class"] == "DA_VERIFICARE"
    assert policy["planner_eligible"] is False
    assert policy["tl_confirmation_required"] is True


def test_aliases_are_normalized():
    assert normalize_operational_class("spare_part") == "RICAMBIO"
    assert normalize_operational_class("solo_riferimento") == "REFERENCE_ONLY"
    assert normalize_operational_class("") == "DA_VERIFICARE"

def test_planner_eligible_standard_does_not_admit_without_active_demand():
    gate = build_planner_admission_gate(
        {
            "operational_class": "STANDARD",
            "route_status": "CERTO",
            "confidence": "CERTO",
        }
    )

    assert gate["planner_eligible"] is True
    assert gate["planner_admitted"] is False
    assert "no_active_customer_order_lot_or_explicit_request" in gate["reasons"]


def test_planner_gate_admits_standard_certain_route_with_active_customer_order():
    gate = build_planner_admission_gate(
        {
            "operational_class": "STANDARD",
            "route_status": "CERTO",
            "confidence": "CERTO",
            "active_customer_order": True,
        }
    )

    assert gate["planner_eligible"] is True
    assert gate["planner_admitted"] is True
    assert gate["reasons"] == []
    assert gate["human_override_allowed"] is True
    assert gate["semantic_gate"]["key"] == "PLANNER_ADMISSION_GATE"


def test_planner_gate_blocks_uncertain_route_even_with_active_demand():
    gate = build_planner_admission_gate(
        {
            "operational_class": "STANDARD",
            "route_status": "DA_VERIFICARE",
            "confidence": "CERTO",
            "explicit_operational_request": True,
        }
    )

    assert gate["planner_admitted"] is False
    assert "route_status_not_certo" in gate["reasons"]


def test_planner_gate_blocks_when_blocking_constraint_is_open():
    gate = build_planner_admission_gate(
        {
            "operational_class": "STANDARD",
            "route_status": "CERTO",
            "confidence": "CERTO",
            "active_lot": True,
            "has_blocking_constraint": True,
        }
    )

    assert gate["planner_admitted"] is False
    assert "blocking_constraint_open" in gate["reasons"]

def test_planner_gate_blocks_12066_without_active_demand():
    gate = build_planner_admission_gate(
        {
            "article": "12066",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route_status": "CERTO",
            "confidence": "CERTO",
            "has_blocking_constraint": False,
        }
    )

    assert gate["planner_admitted"] is False
    assert "no_active_customer_order_lot_or_explicit_request" in gate["reasons"]


def test_planner_gate_admits_12066_with_active_order_and_no_blockers():
    gate = build_planner_admission_gate(
        {
            "article": "12066",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route_status": "CERTO",
            "confidence": "CERTO",
            "active_customer_order": True,
            "has_blocking_constraint": False,
        }
    )

    assert gate["planner_admitted"] is True
    assert gate["reasons"] == []


def test_planner_gate_does_not_block_12058_for_zaw_specificity_note_alone():
    gate = build_planner_admission_gate(
        {
            "article": "12058",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route_status": "CERTO",
            "confidence": "CERTO",
            "active_customer_order": True,
            "zaw_station_specificity": "DA_VERIFICARE",
            "has_blocking_constraint": False,
        }
    )

    assert gate["planner_admitted"] is True
    assert gate["reasons"] == []


def test_planner_gate_blocks_12058_when_zaw_specificity_is_marked_blocking():
    gate = build_planner_admission_gate(
        {
            "article": "12058",
            "operational_class": "STANDARD",
            "planner_eligible": True,
            "route_status": "CERTO",
            "confidence": "CERTO",
            "active_customer_order": True,
            "zaw_station_specificity": "DA_VERIFICARE",
            "has_blocking_constraint": True,
        }
    )

    assert gate["planner_admitted"] is False
    assert "blocking_constraint_open" in gate["reasons"]


def test_planner_admission_gate_metadata_is_registry_backed():
    metadata = _resolve_planner_admission_gate_metadata()

    assert metadata["key"] == "PLANNER_ADMISSION_GATE"
    assert metadata["authority"] == "PROMETEO_MASTER"
    assert "PLANNER-BOUNDARY-001" in metadata["master_refs"]
    assert "operational_class" in metadata["inputs"]
    assert metadata["pass_rule"]
    assert metadata["fail_rule"]


def test_semantic_gate_metadata_does_not_change_admission_result():
    profile = {
        "operational_class": "REFERENCE_ONLY",
        "route_status": "CERTO",
        "confidence": "CERTO",
        "active_customer_order": True,
        "has_blocking_constraint": False,
    }

    gate = build_planner_admission_gate(profile)

    assert gate["planner_eligible"] is True
    assert gate["planner_admitted"] is False
    assert gate["reasons"] == ["operational_class_not_standard"]
    assert gate["rule"] == "STANDARD_CERTAIN_ROUTE_CERTAIN_CONFIDENCE_NO_BLOCKERS_ACTIVE_DEMAND_HUMAN_OVERRIDE"
    assert gate["semantic_gate"]["key"] == "PLANNER_ADMISSION_GATE"
