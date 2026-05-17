"""Deterministic TL semantic eval runner.

Scope:
- no runtime application dependency
- no frontend
- no external AI
- no real production data
- sanitized fixtures only
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticEvalResult:
    passed: bool
    matched_meanings: list[str]
    missing_meanings: list[str]


MEANING_KEYWORDS: dict[str, tuple[str, ...]] = {
    "prioritize_final_pressure_check": (
        "station_cp",
        "controllo finale",
        "chiusura",
    ),
    "do_not_close_without_final_check": (
        "non considerare il lotto chiuso",
        "senza controllo finale",
    ),
    "verify_z1_station_load": (
        "station_z1",
        "verificare il carico",
    ),
    "do_not_escalate_without_blocking_event": (
        "non alzare criticità",
        "evento bloccante",
    ),
    "verify_blocking_event_first": (
        "verificare prima",
        "evento bloccante",
        "station_z1",
    ),
    "do_not_ignore_open_block": (
        "non ignorare",
        "blocco aperto",
    ),
    "keep_final_check_required": (
        "station_cp",
        "obbligatoria",
    ),
}


def normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())


def meaning_matches(answer: str, meaning: str) -> bool:
    normalized = normalize_text(answer)
    keywords = MEANING_KEYWORDS.get(meaning)
    if not keywords:
        return False
    return all(keyword in normalized for keyword in keywords)


def evaluate_answer(answer: str, required_meanings: list[str]) -> SemanticEvalResult:
    matched: list[str] = []
    missing: list[str] = []

    for meaning in required_meanings:
        if meaning_matches(answer, meaning):
            matched.append(meaning)
        else:
            missing.append(meaning)

    return SemanticEvalResult(
        passed=not missing,
        matched_meanings=matched,
        missing_meanings=missing,
    )


def evaluate_case(candidate_answer: str, case: dict) -> SemanticEvalResult:
    return evaluate_answer(
        answer=candidate_answer,
        required_meanings=list(case["required_meanings"]),
    )
