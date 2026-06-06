from app.domain.human_checkpoint import (
    consultation,
    critical_change,
    governance_change,
    informational,
    operational_change,
)


def test_checkpoint_0_informational_requires_no_confirmation():
    checkpoint = informational()

    assert checkpoint.checkpoint_level == 0
    assert checkpoint.risk_level == "LOW"
    assert checkpoint.requires_confirmation is False
    assert checkpoint.confirmation_phrase is None


def test_checkpoint_1_consultation_requires_simple_confirmation():
    checkpoint = consultation()

    assert checkpoint.checkpoint_level == 1
    assert checkpoint.risk_level == "LOW"
    assert checkpoint.requires_confirmation is True
    assert checkpoint.confirmation_phrase == "CONFERMO"


def test_checkpoint_2_operational_change_requires_entity_confirmation():
    checkpoint = operational_change("12097")

    assert checkpoint.checkpoint_level == 2
    assert checkpoint.risk_level == "MEDIUM"
    assert checkpoint.requires_confirmation is True
    assert checkpoint.confirmation_phrase == "CONFERMO MODIFICA 12097"
    assert checkpoint.entity_type == "ARTICLE"
    assert checkpoint.entity_id == "12097"
    assert checkpoint.action == "UPDATE_OPERATIONAL_DATA"


def test_checkpoint_3_critical_change_requires_strong_entity_confirmation():
    checkpoint = critical_change("12097")

    assert checkpoint.checkpoint_level == 3
    assert checkpoint.risk_level == "HIGH"
    assert checkpoint.requires_confirmation is True
    assert checkpoint.confirmation_phrase == "CONFERMO MODIFICA 12097"
    assert checkpoint.entity_type == "ARTICLE"
    assert checkpoint.entity_id == "12097"
    assert checkpoint.action == "UPDATE_SYSTEM_BEHAVIOR"


def test_checkpoint_4_governance_change_requires_governance_confirmation():
    checkpoint = governance_change()

    assert checkpoint.checkpoint_level == 4
    assert checkpoint.risk_level == "CRITICAL"
    assert checkpoint.requires_confirmation is True
    assert checkpoint.confirmation_phrase == "CONFERMO GOVERNANCE"
    assert checkpoint.entity_type == "GOVERNANCE"
    assert checkpoint.action == "UPDATE_GOVERNANCE_CONTRACT"
