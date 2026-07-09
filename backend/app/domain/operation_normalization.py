from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re


PRESSURE_TEST_NORMALIZATION_RULE = "OPERATION_COLLAUDO_PRESSIONE_CONFIRMED_NORMALIZATION"


@dataclass(frozen=True)
class OperationNormalizationResult:
    original_value: str
    normalized_value: str
    applied_rules: tuple[str, ...]


def normalize_operation_value(value: Any) -> OperationNormalizationResult:
    original = "" if value is None else str(value)
    trimmed = original.strip()
    collapsed = re.sub(r"\s+", " ", trimmed)
    comparison = collapsed.upper().rstrip(":.")
    rules: list[str] = []

    if trimmed != original:
        rules.append("VALUE_TRIM")
    if collapsed != trimmed:
        rules.append("VALUE_SPACES_COLLAPSED")

    if comparison == "COLLAUDO A PRESSIONE":
        rules.append(PRESSURE_TEST_NORMALIZATION_RULE)
        return OperationNormalizationResult(
            original_value=original,
            normalized_value="COLLAUDO A PRESSIONE VERTICALE",
            applied_rules=tuple(rules),
        )

    return OperationNormalizationResult(
        original_value=original,
        normalized_value=collapsed,
        applied_rules=tuple(rules),
    )
