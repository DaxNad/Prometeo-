from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HumanCheckpoint:
    checkpoint_level: int
    risk_level: str
    requires_confirmation: bool
    confirmation_phrase: str | None
    entity_type: str | None = None
    entity_id: str | None = None
    action: str | None = None


def informational() -> HumanCheckpoint:
    return HumanCheckpoint(
        checkpoint_level=0,
        risk_level="LOW",
        requires_confirmation=False,
        confirmation_phrase=None,
    )


def consultation() -> HumanCheckpoint:
    return HumanCheckpoint(
        checkpoint_level=1,
        risk_level="LOW",
        requires_confirmation=True,
        confirmation_phrase="CONFERMO",
    )


def operational_change(
    entity_id: str,
    *,
    entity_type: str = "ARTICLE",
    action: str = "UPDATE_OPERATIONAL_DATA",
) -> HumanCheckpoint:
    return HumanCheckpoint(
        checkpoint_level=2,
        risk_level="MEDIUM",
        requires_confirmation=True,
        confirmation_phrase=f"CONFERMO MODIFICA {entity_id}",
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
    )


def critical_change(
    entity_id: str,
    *,
    entity_type: str = "ARTICLE",
    action: str = "UPDATE_SYSTEM_BEHAVIOR",
) -> HumanCheckpoint:
    return HumanCheckpoint(
        checkpoint_level=3,
        risk_level="HIGH",
        requires_confirmation=True,
        confirmation_phrase=f"CONFERMO MODIFICA {entity_id}",
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
    )


def governance_change(
    *,
    action: str = "UPDATE_GOVERNANCE_CONTRACT",
) -> HumanCheckpoint:
    return HumanCheckpoint(
        checkpoint_level=4,
        risk_level="CRITICAL",
        requires_confirmation=True,
        confirmation_phrase="CONFERMO GOVERNANCE",
        entity_type="GOVERNANCE",
        entity_id=None,
        action=action,
    )
