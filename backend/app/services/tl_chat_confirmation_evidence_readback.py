from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any


FOUND = "CONFIRMATION_EVIDENCE_FOUND"
MISSING = "CONFIRMATION_EVIDENCE_MISSING"
INVALID = "INVALID_CONFIRMATION_EVIDENCE"
REJECTED = "OPERATIONAL_PROMOTION_REJECTED"
INVALID_ARTICLE = "INVALID_ARTICLE_CODE"

SAFE_ARTICLE_RE = re.compile(r"^\d{5}[A-Z]{0,3}$")


@dataclass(frozen=True)
class ConfirmationEvidenceReadback:
    article: str
    found: bool
    status: str
    confidence: str = "DA_VERIFICARE"
    requires_confirmation: bool = True
    planner_eligible: bool = False
    promoted_to_certo: bool = False
    requires_persistence_review: bool = True
    confirmed_fields: tuple[str, ...] = field(default_factory=tuple)
    missing_data: tuple[str, ...] = field(default_factory=tuple)
    rendered_text: str = ""


def build_confirmation_evidence_readback(
    *,
    article: str,
    confirmation_root: Path,
) -> ConfirmationEvidenceReadback:
    code = _normalize(article)
    if not SAFE_ARTICLE_RE.fullmatch(code):
        return _closed(code, INVALID_ARTICLE, ("safe article code",))

    path = confirmation_root / f"{code}_confirmation.json"
    if not path.exists():
        return ConfirmationEvidenceReadback(
            article=code,
            found=False,
            status=MISSING,
            missing_data=("confirmation evidence",),
            rendered_text=_render_missing(code),
        )

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _closed(code, INVALID, ("valid json",))

    if not isinstance(record, dict):
        return _closed(code, INVALID, ("object record",))

    return _from_record(code, record)


def _from_record(code: str, record: dict[str, Any]) -> ConfirmationEvidenceReadback:
    schema = _clean(record.get("schema"))
    if schema not in {"TL_CHAT_CONFIRMATION_RECORD_V1", f"TL_CHAT_{code}_CONFIRMATION_RECORD_V1"}:
        return _closed(code, INVALID, ("valid schema",))

    if _normalize(record.get("article")) != code:
        return _closed(code, INVALID, ("matching article",))

    if _clean(record.get("confirmation_status")) != "TL_CONFIRMED_PREVIEW":
        return _closed(code, INVALID, ("TL_CONFIRMED_PREVIEW",))

    if _clean(record.get("confidence")).upper() != "DA_VERIFICARE":
        return _closed(code, REJECTED, ("confidence = DA_VERIFICARE",))

    if bool(record.get("requires_persistence_review", True)) is not True:
        return _closed(code, REJECTED, ("requires_persistence_review = true",))

    if bool(record.get("planner_eligible", False)):
        return _closed(code, REJECTED, ("planner_eligible = false",))

    if bool(record.get("promoted_to_certo", False)):
        return _closed(code, REJECTED, ("promoted_to_certo = false",))

    fields = record.get("confirmed_fields")
    if not isinstance(fields, list):
        fields = []
    clean_fields = tuple(item for item in (_clean(value) for value in fields) if item)

    return ConfirmationEvidenceReadback(
        article=code,
        found=True,
        status=FOUND,
        confirmed_fields=clean_fields,
        rendered_text=_render_found(code, clean_fields),
    )


def _closed(code: str, status: str, missing: tuple[str, ...]) -> ConfirmationEvidenceReadback:
    return ConfirmationEvidenceReadback(
        article=code,
        found=False,
        status=status,
        missing_data=missing,
        rendered_text=(
            f"Articolo: {code}\n"
            f"Evidenza TL persistita: non utilizzabile ({status})\n"
            "confidence=DA_VERIFICARE\n"
            "requires_confirmation=true\n"
            "requires_persistence_review=true\n"
            "planner_eligible=false\n"
            "promoted_to_certo=false"
        ),
    )


def _render_found(code: str, fields: tuple[str, ...]) -> str:
    return "\n".join(
        [
            f"Articolo: {code}",
            "Evidenza TL persistita: presente",
            "confirmation_status: TL_CONFIRMED_PREVIEW",
            "confidence=DA_VERIFICARE",
            "requires_confirmation=true",
            "requires_persistence_review=true",
            "planner_eligible=false",
            "promoted_to_certo=false",
            f"confirmed_fields: {', '.join(fields) if fields else 'none'}",
            "Limite: confirmation evidence is not operational truth.",
            "Prossima azione sicura: mantenere DA_VERIFICARE fino a review di persistenza.",
        ]
    )


def _render_missing(code: str) -> str:
    return "\n".join(
        [
            f"Articolo: {code}",
            "Evidenza TL persistita: assente",
            "confidence=DA_VERIFICARE",
            "requires_confirmation=true",
            "requires_persistence_review=true",
            "planner_eligible=false",
            "promoted_to_certo=false",
            "Prossima azione sicura: mantenere candidate-only fallback.",
        ]
    )


def _normalize(value: Any) -> str:
    return str(value or "").strip().upper()


def _clean(value: Any) -> str:
    return str(value or "").strip()
