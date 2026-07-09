from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

from app.domain.authority_roles import ALLOWED_AUTHORITY_ROLES, normalize_authority_role
from app.domain.intake_classification_vocabulary import (
    ARTICLE_FIELD_ALIASES,
    COMPONENT_FIELD_ALIASES,
    CONSTRAINT_FIELD_ALIASES,
    CONSTRAINT_TERMS,
    GENERIC_CONFIRMATION_MARKERS,
    HISTORICAL_NOTE_MARKERS,
    HUMAN_CONFIRMATION_FIELD_ALIASES,
    OPERATION_TOOL_AMBIGUOUS_VALUES,
    QUALITY_DEFINITION_MARKERS,
    QUALITY_FIELD_ALIASES,
    QUALITY_PHRASES,
    ROUTE_FIELD_ALIASES,
    ROUTE_OPERATIONS,
    TOOL_FIELD_ALIASES,
    TOOL_TERMS,
    comparison_token,
)
from app.domain.operation_normalization import normalize_operation_value


ERROR_INVALID_INPUT = "INVALID_INPUT"
ERROR_INVALID_SCALAR_INPUT = "INVALID_SCALAR_INPUT"
ERROR_MISSING_SOURCE_ID = "MISSING_SOURCE_ID"
ERROR_UNSUPPORTED_VALUE_TYPE = "UNSUPPORTED_VALUE_TYPE"
ERROR_UNCLASSIFIED = "UNCLASSIFIED"
ERROR_AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"
ERROR_CONFLICTING_RULES = "CONFLICTING_RULES"
ERROR_UNAUTHORIZED_AUTHORITY_ROLE = "UNAUTHORIZED_AUTHORITY_ROLE"
ERROR_INCOMPLETE_HUMAN_CONFIRMATION = "INCOMPLETE_HUMAN_CONFIRMATION"

CONFIDENCE_DETERMINISTIC = "DETERMINISTIC_MATCH"
CONFIDENCE_AMBIGUOUS = "AMBIGUOUS_MATCH"
CONFIDENCE_UNCLASSIFIED = "UNCLASSIFIED"
CONFIDENCE_INVALID = "INVALID_INPUT"
CONFIDENCE_CONFLICTING = "CONFLICTING_RULES"


class IntakeDestination(str, Enum):
    ARTICLE = "ARTICLE"
    ROUTE = "ROUTE"
    COMPONENTS = "COMPONENTS"
    TOOLS = "TOOLS"
    QUALITY_CONTROLS = "QUALITY_CONTROLS"
    CONSTRAINTS = "CONSTRAINTS"
    HUMAN_CONFIRMATIONS = "HUMAN_CONFIRMATIONS"


@dataclass(frozen=True)
class IntakeItem:
    field_name: str
    value: Any
    source_id: str
    source_type: str | None = None
    source_status: str | None = None
    semantic_status: str | None = None
    authority_role: str | None = None
    document_section: str | None = None
    document_label: str | None = None
    context: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class IntakeClassificationResult:
    ok: bool
    destination: IntakeDestination | None
    classification_code: str
    matched_rules: tuple[str, ...]
    candidate_destinations: tuple[IntakeDestination, ...]
    original_value: Any
    normalized_value: Any
    normalization_rules_applied: tuple[str, ...]
    requires_review: bool
    review_reason: str | None
    source_id: str
    confidence: str = CONFIDENCE_DETERMINISTIC
    normalized_field_name: str = ""
    error_code: str | None = None


@dataclass(frozen=True)
class RuleStrength(str, Enum):
    STRONG = "STRONG"
    WEAK = "WEAK"


@dataclass(frozen=True)
class _RuleMatch:
    rule_id: str
    priority: int
    destination: IntakeDestination
    classification_code: str
    strength: RuleStrength = RuleStrength.STRONG


def classify_intake_destination(item: IntakeItem) -> IntakeClassificationResult:
    if not isinstance(item, IntakeItem):
        return _invalid_result(
            classification_code=ERROR_INVALID_INPUT,
            error_code=ERROR_INVALID_INPUT,
            source_id="",
            original_value=None,
        )

    source_id = _clean(item.source_id)
    original_value = item.value
    normalized_field_name, field_rules = _normalize_field_name(item.field_name)

    if not source_id:
        return _invalid_result(
            classification_code=ERROR_MISSING_SOURCE_ID,
            error_code=ERROR_MISSING_SOURCE_ID,
            source_id="",
            original_value=original_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=field_rules,
        )

    if _is_scalar_sequence(original_value):
        return _invalid_result(
            classification_code=ERROR_INVALID_SCALAR_INPUT,
            error_code=ERROR_INVALID_SCALAR_INPUT,
            source_id=source_id,
            original_value=original_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=field_rules,
        )

    if not normalized_field_name and _is_empty_value(original_value):
        return _invalid_result(
            classification_code=ERROR_INVALID_INPUT,
            error_code=ERROR_INVALID_INPUT,
            source_id=source_id,
            original_value=original_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=field_rules,
        )

    if _unsupported_value_type(original_value):
        return _invalid_result(
            classification_code=ERROR_UNSUPPORTED_VALUE_TYPE,
            error_code=ERROR_UNSUPPORTED_VALUE_TYPE,
            source_id=source_id,
            original_value=original_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=field_rules,
        )

    authority_role = normalize_authority_role(item.authority_role)
    if authority_role and authority_role not in ALLOWED_AUTHORITY_ROLES:
        return _invalid_result(
            classification_code=ERROR_UNAUTHORIZED_AUTHORITY_ROLE,
            error_code=ERROR_UNAUTHORIZED_AUTHORITY_ROLE,
            source_id=source_id,
            original_value=original_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=field_rules,
        )

    normalized_value, value_rules = _normalize_value(original_value)
    normalization_rules = field_rules + value_rules
    if _human_confirmation_signal_present(item) and not _is_complete_human_confirmation(item, normalized_field_name):
        return IntakeClassificationResult(
            ok=True,
            destination=None,
            classification_code=ERROR_INCOMPLETE_HUMAN_CONFIRMATION,
            matched_rules=("HUMAN_CONFIRMATION_SIGNAL_INCOMPLETE",),
            candidate_destinations=(IntakeDestination.HUMAN_CONFIRMATIONS,),
            original_value=original_value,
            normalized_value=normalized_value,
            normalization_rules_applied=normalization_rules,
            requires_review=True,
            review_reason="Human confirmation signal is missing authority, subject, confirmed field, value, origin, or audit evidence.",
            source_id=source_id,
            confidence=CONFIDENCE_UNCLASSIFIED,
            normalized_field_name=normalized_field_name,
            error_code=ERROR_INCOMPLETE_HUMAN_CONFIRMATION,
        )
    matches = _collect_matches(
        item=item,
        normalized_field_name=normalized_field_name,
        normalized_value=normalized_value,
    )

    if not matches:
        ambiguity = _operation_tool_ambiguity(
            source_id=source_id,
            original_value=original_value,
            normalized_value=normalized_value,
            normalized_field_name=normalized_field_name,
            normalization_rules_applied=normalization_rules,
        )
        if ambiguity is not None:
            return ambiguity

        return IntakeClassificationResult(
            ok=True,
            destination=None,
            classification_code=ERROR_UNCLASSIFIED,
            matched_rules=(),
            candidate_destinations=(),
            original_value=original_value,
            normalized_value=normalized_value,
            normalization_rules_applied=normalization_rules,
            requires_review=True,
            review_reason="No deterministic intake destination rule matched.",
            source_id=source_id,
            confidence=CONFIDENCE_UNCLASSIFIED,
            normalized_field_name=normalized_field_name,
            error_code=ERROR_UNCLASSIFIED,
        )

    ambiguity = _ambiguous_weak_tool_match(
        matches=matches,
        source_id=source_id,
        original_value=original_value,
        normalized_value=normalized_value,
        normalized_field_name=normalized_field_name,
        normalization_rules_applied=normalization_rules,
    )
    if ambiguity is not None:
        return ambiguity

    top_priority = min(match.priority for match in matches)
    top_matches = [match for match in matches if match.priority == top_priority]
    top_destinations = _unique_destinations(match.destination for match in top_matches)
    all_destinations = _unique_destinations(match.destination for match in matches)

    if len(top_destinations) > 1:
        return IntakeClassificationResult(
            ok=True,
            destination=None,
            classification_code=ERROR_CONFLICTING_RULES,
            matched_rules=tuple(match.rule_id for match in matches),
            candidate_destinations=all_destinations,
            original_value=original_value,
            normalized_value=normalized_value,
            normalization_rules_applied=normalization_rules,
            requires_review=True,
            review_reason="Strong rules with the same priority selected different destinations.",
            source_id=source_id,
            confidence=CONFIDENCE_CONFLICTING,
            normalized_field_name=normalized_field_name,
            error_code=ERROR_CONFLICTING_RULES,
        )

    selected = top_matches[0]
    return IntakeClassificationResult(
        ok=True,
        destination=selected.destination,
        classification_code=selected.classification_code,
        matched_rules=tuple(match.rule_id for match in matches),
        candidate_destinations=(selected.destination,),
        original_value=original_value,
        normalized_value=normalized_value,
        normalization_rules_applied=normalization_rules,
        requires_review=False,
        review_reason=None,
        source_id=source_id,
        confidence=CONFIDENCE_DETERMINISTIC,
        normalized_field_name=normalized_field_name,
        error_code=None,
    )


def classify_intake_items(items: Sequence[IntakeItem]) -> list[IntakeClassificationResult]:
    return [classify_intake_destination(item) for item in items]


def _collect_matches(
    *,
    item: IntakeItem,
    normalized_field_name: str,
    normalized_value: Any,
) -> list[_RuleMatch]:
    matches: list[_RuleMatch] = []
    value_token = _comparison_token(normalized_value)
    declared_type = _declared_type(item)
    confirmation_origin = _governed_token(_lookup(item, "confirmation_origin"))
    source_type = _comparison_token(item.source_type)

    if _is_complete_human_confirmation(item, normalized_field_name):
        matches.append(
            _RuleMatch(
                "STRUCTURED_HUMAN_CONFIRMATION",
                20,
                IntakeDestination.HUMAN_CONFIRMATIONS,
                "HUMAN_CONFIRMATION_STRUCTURED",
            )
        )

    if _is_quality_value(item, normalized_field_name, declared_type, value_token):
        matches.append(
            _RuleMatch(
                "QUALITY_OPERATION_EXACT_MATCH",
                35,
                IntakeDestination.QUALITY_CONTROLS,
                "OPERATION_QUALITY_CONTROL",
            )
        )

    for rule_id, destination in _section_matches(item.document_section, "DOCUMENT_SECTION"):
        matches.append(_RuleMatch(rule_id, 50, destination, _classification_code(destination, "DOCUMENT_SECTION")))

    for rule_id, destination in _section_matches(item.document_label, "DOCUMENT_LABEL"):
        matches.append(_RuleMatch(rule_id, 50, destination, _classification_code(destination, "DOCUMENT_LABEL")))

    field_match = _field_match(normalized_field_name)
    if field_match is not None:
        rule_id, destination = field_match
        matches.append(_RuleMatch(rule_id, 40, destination, _classification_code(destination, "FIELD_ALIAS")))

    type_match = _type_match(declared_type)
    if type_match is not None:
        rule_id, destination = type_match
        matches.append(_RuleMatch(rule_id, 30, destination, _classification_code(destination, "DECLARED_TYPE")))

    if value_token in ROUTE_OPERATIONS:
        matches.append(
            _RuleMatch(
                "ROUTE_OPERATION_EXACT_MATCH",
                60,
                IntakeDestination.ROUTE,
                "ROUTE_OPERATION_EXACT",
            )
        )

    if _is_tool_value(value_token):
        matches.append(_RuleMatch("TOOL_LEXICAL_MATCH", 70, IntakeDestination.TOOLS, "TOOL_LEXICAL"))

    if _is_constraint_value(value_token):
        matches.append(
            _RuleMatch("CONSTRAINT_LEXICAL_MATCH", 25, IntakeDestination.CONSTRAINTS, "CONSTRAINT_LEXICAL")
        )

    if _looks_like_component_code(value_token) and _component_context(item, normalized_field_name, declared_type):
        matches.append(
            _RuleMatch(
                "COMPONENT_CODE_DECLARED_CONTEXT",
                60,
                IntakeDestination.COMPONENTS,
                "COMPONENT_CODE_DECLARED",
            )
        )

    return matches


def _field_match(normalized_field_name: str) -> tuple[str, IntakeDestination] | None:
    if normalized_field_name in ARTICLE_FIELD_ALIASES:
        return "ARTICLE_FIELD_ALIAS", IntakeDestination.ARTICLE
    if normalized_field_name in ROUTE_FIELD_ALIASES:
        return "ROUTE_FIELD_ALIAS", IntakeDestination.ROUTE
    if normalized_field_name in COMPONENT_FIELD_ALIASES:
        return "COMPONENT_FIELD_ALIAS", IntakeDestination.COMPONENTS
    if normalized_field_name in TOOL_FIELD_ALIASES:
        return "TOOL_FIELD_ALIAS", IntakeDestination.TOOLS
    if normalized_field_name in QUALITY_FIELD_ALIASES:
        return "QUALITY_FIELD_ALIAS", IntakeDestination.QUALITY_CONTROLS
    if normalized_field_name in CONSTRAINT_FIELD_ALIASES:
        return "CONSTRAINT_FIELD_ALIAS", IntakeDestination.CONSTRAINTS
    if normalized_field_name in HUMAN_CONFIRMATION_FIELD_ALIASES:
        return "HUMAN_CONFIRMATION_FIELD_ALIAS", IntakeDestination.HUMAN_CONFIRMATIONS
    return None


def _type_match(declared_type: str) -> tuple[str, IntakeDestination] | None:
    if declared_type in {"TOOL", "TOOLS", "TOOLING", "MACHINE", "MACCHINA", "ATTREZZATURA", "FIXTURE"}:
        return "TOOLS_DECLARED_TYPE", IntakeDestination.TOOLS
    if declared_type in {"COMPONENT", "COMPONENTE", "BOM_ITEM", "PART"}:
        return "COMPONENT_DECLARED_TYPE", IntakeDestination.COMPONENTS
    if declared_type in {"ARTICLE", "ARTICOLO"}:
        return "ARTICLE_DECLARED_TYPE", IntakeDestination.ARTICLE
    if declared_type in {"QUALITY_CONTROL", "COLLAUDO", "CONTROLLO"}:
        return "QUALITY_DECLARED_TYPE", IntakeDestination.QUALITY_CONTROLS
    if declared_type in {"CONSTRAINT", "VINCOLO"}:
        return "CONSTRAINT_DECLARED_TYPE", IntakeDestination.CONSTRAINTS
    return None


def _section_matches(value: Any, prefix: str) -> list[tuple[str, IntakeDestination]]:
    token = _comparison_token(value)
    if not token:
        return []

    destinations: list[tuple[str, IntakeDestination]] = []
    if token in {"ARTICOLO", "ARTICLE", "ANAGRAFICA", "IDENTIFICAZIONE"}:
        destinations.append((f"{prefix}_ARTICLE", IntakeDestination.ARTICLE))
    if token in {"OPERAZIONI", "ROUTE", "CICLO", "FASI", "OPERATIONS"}:
        destinations.append((f"{prefix}_OPERATIONS", IntakeDestination.ROUTE))
    if token in {"COMPONENTI", "DISTINTA", "BOM", "MATERIALI"}:
        destinations.append((f"{prefix}_COMPONENTS", IntakeDestination.COMPONENTS))
    if token in {"ATTREZZATURE", "TOOLS", "TOOLING", "MACCHINE", "UTENSILI"}:
        destinations.append((f"{prefix}_TOOLS", IntakeDestination.TOOLS))
    if token in {"COLLAUDI", "CONTROLLI", "QUALITA", "QUALITY", "QUALITY_CONTROLS"}:
        destinations.append((f"{prefix}_QUALITY", IntakeDestination.QUALITY_CONTROLS))
    if token in {"VINCOLI", "CONSTRAINTS", "LIMITI", "CONDIZIONI"}:
        destinations.append((f"{prefix}_CONSTRAINTS", IntakeDestination.CONSTRAINTS))
    return destinations


def _classification_code(destination: IntakeDestination, source: str) -> str:
    return f"{destination.value}_{source}"


def _operation_tool_ambiguity(
    *,
    source_id: str,
    original_value: Any,
    normalized_value: Any,
    normalized_field_name: str,
    normalization_rules_applied: tuple[str, ...],
) -> IntakeClassificationResult | None:
    value_token = _comparison_token(normalized_value)
    if value_token not in OPERATION_TOOL_AMBIGUOUS_VALUES:
        return None

    return IntakeClassificationResult(
        ok=True,
        destination=None,
        classification_code="AMBIGUOUS_OPERATION_OR_TOOL",
        matched_rules=("WEAK_OPERATION_TOOL_AMBIGUITY",),
        candidate_destinations=(IntakeDestination.ROUTE, IntakeDestination.TOOLS),
        original_value=original_value,
        normalized_value=normalized_value,
        normalization_rules_applied=normalization_rules_applied,
        requires_review=True,
        review_reason="Value can represent either an operation or a tool; context is insufficient.",
        source_id=source_id,
        confidence=CONFIDENCE_AMBIGUOUS,
        normalized_field_name=normalized_field_name,
        error_code=ERROR_AMBIGUOUS_MATCH,
    )


def _ambiguous_weak_tool_match(
    *,
    matches: list[_RuleMatch],
    source_id: str,
    original_value: Any,
    normalized_value: Any,
    normalized_field_name: str,
    normalization_rules_applied: tuple[str, ...],
) -> IntakeClassificationResult | None:
    value_token = _comparison_token(normalized_value)
    if value_token not in OPERATION_TOOL_AMBIGUOUS_VALUES:
        return None

    contextual_matches = [
        match
        for match in matches
        if match.destination in {IntakeDestination.ROUTE, IntakeDestination.TOOLS}
        and match.rule_id
        in {
            "DOCUMENT_SECTION_OPERATIONS",
            "DOCUMENT_LABEL_OPERATIONS",
            "TOOL_FIELD_ALIAS",
            "TOOLS_DECLARED_TYPE",
        }
    ]
    if contextual_matches:
        return None

    return _operation_tool_ambiguity(
        source_id=source_id,
        original_value=original_value,
        normalized_value=normalized_value,
        normalized_field_name=normalized_field_name,
        normalization_rules_applied=normalization_rules_applied,
    )


def _normalize_field_name(value: Any) -> tuple[str, tuple[str, ...]]:
    text = _clean(value)
    if not text:
        return "", ()

    rules: list[str] = []
    stripped = text.strip()
    if stripped != text:
        rules.append("FIELD_NAME_TRIM")

    lowered = stripped.casefold()
    if lowered != stripped:
        rules.append("FIELD_NAME_CASEFOLD")

    normalized = re.sub(r"[\s\-]+", "_", lowered)
    if normalized != lowered:
        rules.append("FIELD_NAME_SEPARATOR_NORMALIZED")

    return normalized, tuple(rules)


def _normalize_value(value: Any) -> tuple[Any, tuple[str, ...]]:
    if isinstance(value, Mapping):
        value = _display_value_from_mapping(value)

    if not isinstance(value, str):
        return value, ()

    result = normalize_operation_value(value)
    return result.normalized_value, result.applied_rules


def _display_value_from_mapping(value: Mapping[str, Any]) -> Any:
    for key in (
        "value",
        "code",
        "codice",
        "component",
        "component_code",
        "article",
        "articolo",
        "name",
        "label",
        "operation",
        "operazione",
        "description",
        "descrizione",
    ):
        candidate = value.get(key)
        if not _is_empty_value(candidate):
            return candidate
    return ""


def _declared_type(item: IntakeItem) -> str:
    for container in (item.metadata, item.context, item.value if isinstance(item.value, Mapping) else None):
        if not isinstance(container, Mapping):
            continue
        for key in ("entity_type", "type", "tipo", "value_type", "field_type"):
            value = container.get(key)
            token = _comparison_token(value)
            if token:
                return token
    return ""


def _lookup(item: IntakeItem, key: str) -> Any:
    for container in (item.metadata, item.context, item.value if isinstance(item.value, Mapping) else None):
        if isinstance(container, Mapping) and key in container:
            return container[key]
    return None


def _human_confirmation_signal_present(item: IntakeItem) -> bool:
    declared_type = _declared_type(item)
    return (
        _comparison_token(item.source_type) == "HUMAN_OPERATIONAL_CONFIRMATION"
        or normalize_authority_role(item.authority_role) in ALLOWED_AUTHORITY_ROLES
        or _governed_token(_lookup(item, "confirmation_origin")) == "HUMAN_EXPLICIT_CONFIRMATION"
        or declared_type in {"HUMAN_CONFIRMATION", "OPERATIONAL_CONFIRMATION"}
    )


def _is_complete_human_confirmation(item: IntakeItem, normalized_field_name: str) -> bool:
    if not _human_confirmation_signal_present(item):
        return False

    has_authority = normalize_authority_role(item.authority_role) in ALLOWED_AUTHORITY_ROLES
    has_origin = _governed_token(_lookup(item, "confirmation_origin")) == "HUMAN_EXPLICIT_CONFIRMATION"
    has_subject = any(
        not _is_empty_value(_lookup(item, key))
        for key in ("subject", "article", "articolo", "entity_id")
    )
    has_field = bool(normalized_field_name) or any(
        not _is_empty_value(_lookup(item, key))
        for key in ("confirmed_field", "field_name")
    )
    has_value = not _is_empty_value(item.value) or any(
        not _is_empty_value(_lookup(item, key))
        for key in ("confirmed_value", "value")
    )
    has_audit = any(
        not _is_empty_value(_lookup(item, key))
        for key in ("audit_note", "evidence", "evidence_id")
    )
    return has_authority and has_origin and has_subject and has_field and has_value and has_audit


def _is_quality_value(
    item: IntakeItem,
    normalized_field_name: str,
    declared_type: str,
    value_token: str,
) -> bool:
    if not value_token:
        return False
    if _is_constraint_value(value_token):
        return False
    if normalized_field_name in TOOL_FIELD_ALIASES or declared_type in {
        "TOOL",
        "TOOLS",
        "TOOLING",
        "MACHINE",
        "MACCHINA",
        "ATTREZZATURA",
        "FIXTURE",
    }:
        return False
    if any(destination == IntakeDestination.TOOLS for _, destination in _section_matches(item.document_section, "DOCUMENT_SECTION")):
        return False
    if normalized_field_name in COMPONENT_FIELD_ALIASES or declared_type in {
        "COMPONENT",
        "COMPONENTE",
        "BOM_ITEM",
        "PART",
    }:
        return False
    if any(destination == IntakeDestination.COMPONENTS for _, destination in _section_matches(item.document_section, "DOCUMENT_SECTION")):
        return False
    if any(marker in value_token for marker in HISTORICAL_NOTE_MARKERS):
        return False
    if any(marker in value_token for marker in GENERIC_CONFIRMATION_MARKERS):
        return False
    if value_token in {"CONTROLLO", "PRESSIONE"}:
        return False
    return any(term in value_token for term in QUALITY_PHRASES) or any(
        marker in value_token for marker in QUALITY_DEFINITION_MARKERS
    )


def _is_tool_value(value_token: str) -> bool:
    if not value_token:
        return False
    if any(term in value_token for term in TOOL_TERMS):
        return True
    return bool(re.fullmatch(r"(CRT|CRM)\d+[A-Z0-9]*", value_token))


def _is_constraint_value(value_token: str) -> bool:
    if not value_token:
        return False
    return any(term in value_token for term in CONSTRAINT_TERMS)


def _looks_like_component_code(value_token: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]{3,}", value_token))


def _component_context(item: IntakeItem, normalized_field_name: str, declared_type: str) -> bool:
    if normalized_field_name in COMPONENT_FIELD_ALIASES:
        return True
    if declared_type in {"COMPONENT", "COMPONENTE", "BOM_ITEM", "PART"}:
        return True
    section_destinations = _section_matches(item.document_section, "DOCUMENT_SECTION")
    return any(destination == IntakeDestination.COMPONENTS for _, destination in section_destinations)


def _invalid_result(
    *,
    classification_code: str,
    error_code: str,
    source_id: str,
    original_value: Any,
    normalized_field_name: str = "",
    normalization_rules_applied: tuple[str, ...] = (),
) -> IntakeClassificationResult:
    return IntakeClassificationResult(
        ok=False,
        destination=None,
        classification_code=classification_code,
        matched_rules=(),
        candidate_destinations=(),
        original_value=original_value,
        normalized_value=None,
        normalization_rules_applied=normalization_rules_applied,
        requires_review=True,
        review_reason=error_code,
        source_id=source_id,
        confidence=CONFIDENCE_INVALID,
        normalized_field_name=normalized_field_name,
        error_code=error_code,
    )


def _unique_destinations(destinations: Any) -> tuple[IntakeDestination, ...]:
    seen: set[IntakeDestination] = set()
    out: list[IntakeDestination] = []
    for destination in destinations:
        if destination in seen:
            continue
        seen.add(destination)
        out.append(destination)
    return tuple(out)


def _unsupported_value_type(value: Any) -> bool:
    if value is None:
        return False
    return not isinstance(value, (str, int, float, bool, Mapping))


def _is_scalar_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset))


def _is_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not any(not _is_empty_value(candidate) for candidate in value.values())
    return False


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _comparison_token(value: Any) -> str:
    return comparison_token(value)


def _governed_token(value: Any) -> str:
    return _comparison_token(value)
