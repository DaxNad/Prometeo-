from app.domain.operational_class import (
    build_operational_policy,
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
