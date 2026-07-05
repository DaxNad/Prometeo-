"""Non-persistent TL Chat confirmation rendering helpers.

This module is intentionally service-only.

It does not bind to TL Chat API routes.
It does not persist TL answers.
It does not mutate preview JSON.
It does not promote values to CERTO.
It does not enable planner eligibility.
It does not invoke ATLAS.
It does not write to SMF or database.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


SAFE_ARTICLE_RE = re.compile(r"^\d{5}[A-Z]{0,3}$")

ALLOWED_QUESTION_IDS = frozenset({"Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"})

ALLOWED_TL_ANSWER_STATES = frozenset(
    {
        "YES",
        "NO",
        "UNKNOWN",
        "CORRECTED_VALUE",
        "NOT_VISIBLE",
        "ABSENT",
    }
)

ALLOWED_RESULTING_STATUSES = frozenset(
    {
        "CANDIDATE_CONFIRMATION",
        "CANDIDATE_CORRECTION",
        "DA_VERIFICARE",
        "MISSING",
        "BLOCKED",
    }
)

FIELD_GROUP_BY_QUESTION_ID = {
    "Q1": "article_identity",
    "Q2": "packaging_and_quantities",
    "Q3": "normalized_route",
    "Q4": "zaw_station_resolution",
    "Q5": "components",
    "Q6": "tooling",
    "Q7": "pidmill_and_cp_visibility",
}

RUNTIME_EFFECTS_STATEMENT = (
    "Effetti runtime: nessuna persistenza, nessuna mutazione sorgente, "
    "nessuna promozione a CERTO, nessun planner, nessun ATLAS, "
    "nessuna scrittura SMF/DB."
)

FORBIDDEN_RUNTIME_EFFECTS = {
    "tl_answer_persistence": False,
    "preview_json_mutation": False,
    "certo_promotion": False,
    "planner_enablement": False,
    "atlas_invocation": False,
    "smf_write": False,
    "database_write": False,
    "api_contract_change": False,
    "production_readiness": False,
    "planning_readiness": False,
}


@dataclass(frozen=True)
class TLChatConfirmationRenderingInput:
    """Input for a non-persistent TL Chat confirmation rendering candidate."""

    article: str
    question_id: str
    tl_answer_state: str
    resulting_status: str
    candidate_data: dict[str, Any]
    missing_data: list[str]
    next_safe_action: str
    corrected_value: dict[str, Any] | None = None


@dataclass(frozen=True)
class TLChatConfirmationRenderingResult:
    """Rendered non-persistent TL Chat confirmation response."""

    article: str
    question_id: str
    field_group: str
    tl_answer_state: str
    resulting_status: str
    candidate_data: dict[str, Any]
    corrected_value: dict[str, Any] | None
    confidence: str
    missing_data: list[str]
    runtime_effects: str
    forbidden_runtime_effects: dict[str, bool]
    next_safe_action: str
    rendered_text: str


class TLChatConfirmationRenderingError(ValueError):
    """Raised when a rendering candidate violates the governed contract."""


def build_confirmation_rendering(
    data: TLChatConfirmationRenderingInput,
) -> TLChatConfirmationRenderingResult:
    """Build a non-persistent TL Chat confirmation rendering result.

    The returned object is a display candidate only.
    It is not source of truth and has no operational side effects.
    """

    _validate_input(data)

    field_group = FIELD_GROUP_BY_QUESTION_ID[data.question_id]
    missing_data = list(data.missing_data)
    candidate_data = dict(data.candidate_data)
    corrected_value = (
        dict(data.corrected_value) if data.corrected_value is not None else None
    )

    rendered_text = _render_text(
        article=data.article,
        question_id=data.question_id,
        field_group=field_group,
        tl_answer_state=data.tl_answer_state,
        resulting_status=data.resulting_status,
        candidate_data=candidate_data,
        missing_data=missing_data,
        next_safe_action=data.next_safe_action,
    )

    return TLChatConfirmationRenderingResult(
        article=data.article,
        question_id=data.question_id,
        field_group=field_group,
        tl_answer_state=data.tl_answer_state,
        resulting_status=data.resulting_status,
        candidate_data=candidate_data,
        corrected_value=corrected_value,
        confidence="DA_VERIFICARE",
        missing_data=missing_data,
        runtime_effects=RUNTIME_EFFECTS_STATEMENT,
        forbidden_runtime_effects=dict(FORBIDDEN_RUNTIME_EFFECTS),
        next_safe_action=data.next_safe_action,
        rendered_text=rendered_text,
    )


def _validate_input(data: TLChatConfirmationRenderingInput) -> None:
    if not SAFE_ARTICLE_RE.fullmatch(data.article):
        raise TLChatConfirmationRenderingError("Invalid article code.")

    if data.question_id not in ALLOWED_QUESTION_IDS:
        raise TLChatConfirmationRenderingError("Unsupported question_id.")

    if data.tl_answer_state not in ALLOWED_TL_ANSWER_STATES:
        raise TLChatConfirmationRenderingError("Unsupported tl_answer_state.")

    if data.resulting_status not in ALLOWED_RESULTING_STATUSES:
        raise TLChatConfirmationRenderingError("Unsupported resulting_status.")

    if data.tl_answer_state == "CORRECTED_VALUE" and not data.corrected_value:
        raise TLChatConfirmationRenderingError(
            "CORRECTED_VALUE requires corrected_value."
        )

    if data.tl_answer_state == "ABSENT" and data.question_id != "Q7":
        raise TLChatConfirmationRenderingError("ABSENT is renderable only for Q7.")

    if data.resulting_status in {
        "CERTO",
        "PRODUCTION_READY",
        "PLANNING_READY",
        "PLANNER_ELIGIBLE",
        "SOURCE_OF_TRUTH",
        "SAVED",
        "PERSISTED",
    }:
        raise TLChatConfirmationRenderingError(
            "Operational resulting_status is forbidden."
        )

    if not data.next_safe_action.strip():
        raise TLChatConfirmationRenderingError("next_safe_action is required.")


def _render_text(
    *,
    article: str,
    question_id: str,
    field_group: str,
    tl_answer_state: str,
    resulting_status: str,
    candidate_data: dict[str, Any],
    missing_data: list[str],
    next_safe_action: str,
) -> str:
    candidate_data_text = _format_candidate_data(candidate_data)
    missing_data_text = ", ".join(missing_data) if missing_data else "none"

    return "\n".join(
        [
            f"Articolo: {article}",
            f"Domanda: {question_id} - {field_group}",
            f"Risposta TL: {tl_answer_state}",
            f"Stato risultante: {resulting_status}",
            f"Dati candidati: {candidate_data_text}",
            "Confidenza: DA_VERIFICARE",
            f"Dati mancanti: {missing_data_text}",
            RUNTIME_EFFECTS_STATEMENT,
            f"Prossima azione sicura: {next_safe_action}",
        ]
    )


def _format_candidate_data(candidate_data: dict[str, Any]) -> str:
    if not candidate_data:
        return "none"

    return ", ".join(
        f"{key} {value}" for key, value in sorted(candidate_data.items())
    )