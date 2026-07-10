from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import copy
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from app.domain.authority_roles import ALLOWED_AUTHORITY_ROLES, normalize_authority_role
from app.domain.article_operational_registry import (
    get_article_operational_registry_path,
    get_operational_registry_entry,
    reset_article_operational_registry_cache,
)
from app.domain.operational_class import VALID_OPERATIONAL_CLASSES

ALLOWED_CONFIRMATION_ORIGINS = frozenset({"HUMAN_EXPLICIT_CONFIRMATION"})

ERROR_REGISTRY_NOT_FOUND = "REGISTRY_NOT_FOUND"
ERROR_INVALID_ARTICLE = "INVALID_ARTICLE"
ERROR_INVALID_OPERATIONAL_CLASS = "INVALID_OPERATIONAL_CLASS"
ERROR_INVALID_PLANNER_ELIGIBLE = "INVALID_PLANNER_ELIGIBLE"
ERROR_INVALID_TL_CONFIRMATION_REQUIRED = "INVALID_TL_CONFIRMATION_REQUIRED"
ERROR_UNAUTHORIZED_AUTHORITY = "UNAUTHORIZED_AUTHORITY"
ERROR_INVALID_CONFIRMATION_ORIGIN = "INVALID_CONFIRMATION_ORIGIN"
ERROR_INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
ERROR_AUDIT_NOTE_REQUIRED = "AUDIT_NOTE_REQUIRED"
ERROR_INVALID_REGISTRY = "INVALID_REGISTRY"
ERROR_WRITE_FAILED = "WRITE_FAILED"
ERROR_WRITE_SUCCEEDED_READBACK_FAILED = "WRITE_SUCCEEDED_READBACK_FAILED"
ERROR_INVALID_SOURCE_EVIDENCE = "INVALID_SOURCE_EVIDENCE"

SOURCE_EVIDENCE_FIELDS = frozenset(
    {
        "source_id",
        "source_type",
        "source_status",
        "semantic_status",
        "matched_rules",
    }
)


@dataclass(frozen=True)
class ArticleOperationalConfirmationResult:
    ok: bool
    article: str
    created: bool = False
    updated: bool = False
    previous_record: dict[str, Any] | None = None
    current_record: dict[str, Any] | None = None
    registry_path: str | None = None
    confirmed_at: str | None = None
    error_code: str | None = None
    persisted: bool = False


def confirm_article_operational_status(
    *,
    article: str,
    operational_class: str,
    planner_eligible: bool,
    tl_confirmation_required: bool,
    authority_role: str,
    audit_note: str,
    confirmed_at: datetime | str | None = None,
    material: str | None = None,
    drawing: str | None = None,
    description: str | None = None,
    confirmation_origin: str = "HUMAN_EXPLICIT_CONFIRMATION",
    source_evidence: Mapping[str, Any] | None = None,
) -> ArticleOperationalConfirmationResult:
    code = _normalize_article(article)
    registry_path = get_article_operational_registry_path()
    registry_path_text = str(registry_path) if registry_path is not None else None
    normalized_source_evidence = _normalize_source_evidence(source_evidence)

    if source_evidence is not None and normalized_source_evidence is None:
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=registry_path_text,
            error_code=ERROR_INVALID_SOURCE_EVIDENCE,
        )

    validation_error = _validate_input(
        article=code,
        operational_class=operational_class,
        planner_eligible=planner_eligible,
        tl_confirmation_required=tl_confirmation_required,
        authority_role=authority_role,
        confirmation_origin=confirmation_origin,
        confirmed_at=confirmed_at,
    )
    if validation_error:
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=registry_path_text,
            error_code=validation_error,
        )

    if registry_path is None:
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=None,
            error_code=ERROR_REGISTRY_NOT_FOUND,
        )

    confirmed_at_validation_text = _optional_confirmed_at_text(confirmed_at)
    try:
        registry = _load_registry(registry_path)
    except (OSError, json.JSONDecodeError):
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_validation_text,
            error_code=ERROR_INVALID_REGISTRY,
        )

    articles = registry.get("articles")
    if not isinstance(articles, dict):
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_validation_text,
            error_code=ERROR_INVALID_REGISTRY,
        )

    previous_record = _find_existing_record(articles, code)
    created = previous_record is None

    if created and not audit_note.strip():
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_validation_text,
            error_code=ERROR_AUDIT_NOTE_REQUIRED,
        )

    if previous_record is not None and not _has_substantial_change(
        previous_record=previous_record,
        operational_class=operational_class,
        planner_eligible=planner_eligible,
        tl_confirmation_required=tl_confirmation_required,
        authority_role=authority_role,
        confirmation_origin=confirmation_origin,
        material=material,
        drawing=drawing,
        description=description,
        source_evidence=normalized_source_evidence,
    ):
        existing_confirmed_at = _clean(previous_record.get("confirmed_at"))
        return ArticleOperationalConfirmationResult(
            ok=True,
            article=code,
            created=False,
            updated=False,
            previous_record=copy.deepcopy(previous_record),
            current_record=copy.deepcopy(previous_record),
            registry_path=registry_path_text,
            confirmed_at=existing_confirmed_at or confirmed_at_validation_text,
            persisted=False,
        )

    if previous_record and not audit_note.strip():
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            previous_record=copy.deepcopy(previous_record),
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_validation_text,
            error_code=ERROR_AUDIT_NOTE_REQUIRED,
        )

    confirmed_at_text = _confirmed_at_text(confirmed_at)
    current_record = _build_record(
        code=code,
        previous_record=previous_record,
        operational_class=operational_class,
        planner_eligible=planner_eligible,
        tl_confirmation_required=tl_confirmation_required,
        authority_role=authority_role,
        audit_note=audit_note,
        confirmed_at=confirmed_at_text,
        material=material,
        drawing=drawing,
        description=description,
        confirmation_origin=confirmation_origin,
        source_evidence=normalized_source_evidence,
    )

    updated_registry = copy.deepcopy(registry)
    updated_articles = updated_registry["articles"]
    existing_key = _find_existing_key(updated_articles, code) or code
    updated_articles[existing_key] = current_record
    updated_registry["updated_at"] = confirmed_at_text

    try:
        _atomic_write_json(registry_path, updated_registry)
    except OSError:
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            created=False,
            updated=False,
            previous_record=copy.deepcopy(previous_record),
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_text,
            error_code=ERROR_WRITE_FAILED,
            persisted=False,
        )

    reset_article_operational_registry_cache()
    readback = get_operational_registry_entry(code)
    if readback is None:
        return ArticleOperationalConfirmationResult(
            ok=False,
            article=code,
            previous_record=copy.deepcopy(previous_record),
            current_record=copy.deepcopy(current_record),
            registry_path=registry_path_text,
            confirmed_at=confirmed_at_text,
            error_code=ERROR_WRITE_SUCCEEDED_READBACK_FAILED,
            persisted=True,
        )

    return ArticleOperationalConfirmationResult(
        ok=True,
        article=code,
        created=created,
        updated=not created,
        previous_record=copy.deepcopy(previous_record),
        current_record=copy.deepcopy(readback),
        registry_path=registry_path_text,
        confirmed_at=confirmed_at_text,
        persisted=True,
    )


def _validate_input(
    *,
    article: str,
    operational_class: str,
    planner_eligible: bool,
    tl_confirmation_required: bool,
    authority_role: str,
    confirmation_origin: str,
    confirmed_at: datetime | str | None,
) -> str | None:
    if not article:
        return ERROR_INVALID_ARTICLE

    if _normalize_token(operational_class) not in VALID_OPERATIONAL_CLASSES:
        return ERROR_INVALID_OPERATIONAL_CLASS

    if not isinstance(planner_eligible, bool):
        return ERROR_INVALID_PLANNER_ELIGIBLE

    if not isinstance(tl_confirmation_required, bool):
        return ERROR_INVALID_TL_CONFIRMATION_REQUIRED

    if normalize_authority_role(authority_role) not in ALLOWED_AUTHORITY_ROLES:
        return ERROR_UNAUTHORIZED_AUTHORITY

    if _normalize_token(confirmation_origin) not in ALLOWED_CONFIRMATION_ORIGINS:
        return ERROR_INVALID_CONFIRMATION_ORIGIN

    if confirmed_at is not None:
        try:
            _confirmed_at_text(confirmed_at)
        except ValueError:
            return ERROR_INVALID_TIMESTAMP

    return None


def _load_registry(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_name = tmp.name
            json.dump(data, tmp, ensure_ascii=False, indent=2, sort_keys=True)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        Path(tmp_name).replace(path)
    except OSError:
        if tmp_name:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise


def _build_record(
    *,
    code: str,
    previous_record: dict[str, Any] | None,
    operational_class: str,
    planner_eligible: bool,
    tl_confirmation_required: bool,
    authority_role: str,
    audit_note: str,
    confirmed_at: str,
    material: str | None,
    drawing: str | None,
    description: str | None,
    confirmation_origin: str,
    source_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    record = copy.deepcopy(previous_record) if previous_record else {}
    record.update(
        {
            "operational_class": _normalize_token(operational_class),
            "planner_eligible": planner_eligible,
            "tl_confirmation_required": tl_confirmation_required,
            "source": "human_operational_confirmation",
            "source_authority": _normalize_token(authority_role),
            "authority_role": _normalize_token(authority_role),
            "confirmation_origin": _normalize_token(confirmation_origin),
            "confirmed_at": confirmed_at,
            "audit_note": audit_note.strip(),
        }
    )

    if previous_record is not None:
        history = _existing_confirmation_history(previous_record)
        history_entry = _build_confirmation_history_entry(
            previous_record=previous_record,
            superseded_at=confirmed_at,
            superseded_by_authority=_normalize_token(authority_role),
        )
        if history_entry and _should_append_history(history, history_entry):
            history.append(history_entry)
        if history:
            record["confirmation_history"] = history

    for key, value in (
        ("material", material),
        ("drawing", drawing),
        ("description", description),
    ):
        if value is not None:
            cleaned = str(value).strip()
            if cleaned:
                record[key] = cleaned

    if source_evidence is not None:
        record["source_evidence"] = copy.deepcopy(source_evidence)

    record.setdefault("article", code)
    return record


def _has_substantial_change(
    *,
    previous_record: dict[str, Any],
    operational_class: str,
    planner_eligible: bool,
    tl_confirmation_required: bool,
    authority_role: str,
    confirmation_origin: str,
    material: str | None,
    drawing: str | None,
    description: str | None,
    source_evidence: dict[str, Any] | None,
) -> bool:
    expected = {
        "operational_class": _normalize_token(operational_class),
        "planner_eligible": planner_eligible,
        "tl_confirmation_required": tl_confirmation_required,
        "source_authority": _normalize_token(authority_role),
        "authority_role": _normalize_token(authority_role),
        "confirmation_origin": _normalize_token(confirmation_origin),
    }

    for key, value in expected.items():
        if previous_record.get(key) != value:
            return True

    for key, value in (
        ("material", material),
        ("drawing", drawing),
        ("description", description),
    ):
        if value is not None and str(value).strip() and previous_record.get(key) != str(value).strip():
            return True

    if source_evidence is not None and previous_record.get("source_evidence") != source_evidence:
        return True

    return False


def _build_confirmation_history_entry(
    *,
    previous_record: dict[str, Any],
    superseded_at: str,
    superseded_by_authority: str,
) -> dict[str, Any]:
    entry: dict[str, Any] = {}
    for key in (
        "operational_class",
        "planner_eligible",
        "tl_confirmation_required",
        "source",
        "source_authority",
        "authority_role",
        "confirmation_origin",
        "confirmed_at",
        "audit_note",
        "material",
        "drawing",
        "description",
        "source_evidence",
    ):
        if key in previous_record:
            entry[key] = copy.deepcopy(previous_record[key])

    entry["superseded_at"] = superseded_at
    entry["superseded_by_authority"] = superseded_by_authority
    return entry


def _existing_confirmation_history(record: dict[str, Any]) -> list[dict[str, Any]]:
    raw = record.get("confirmation_history")
    if not isinstance(raw, list):
        return []

    return [copy.deepcopy(item) for item in raw if isinstance(item, dict)]


def _should_append_history(history: list[dict[str, Any]], entry: dict[str, Any]) -> bool:
    if not history:
        return True

    return _history_identity(history[-1]) != _history_identity(entry)


def _history_identity(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in entry.items()
        if key != "confirmation_history"
    }


def _find_existing_key(articles: dict[str, Any], code: str) -> str | None:
    for key in (code, code.strip(), code.upper()):
        if key in articles and isinstance(articles[key], dict):
            return key

    for key, value in articles.items():
        if isinstance(key, str) and _normalize_article(key) == code and isinstance(value, dict):
            return key

    return None


def _find_existing_record(articles: dict[str, Any], code: str) -> dict[str, Any] | None:
    key = _find_existing_key(articles, code)
    if key is None:
        return None
    return copy.deepcopy(articles[key])


def _confirmed_at_text(value: datetime | str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    text = str(value).strip()
    if not text:
        raise ValueError("empty timestamp")

    datetime.fromisoformat(text.replace("Z", "+00:00"))
    return text


def _optional_confirmed_at_text(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    return _confirmed_at_text(value)


def _normalize_article(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_token(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _normalize_source_evidence(
    source_evidence: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if source_evidence is None:
        return None
    if not isinstance(source_evidence, Mapping):
        return None
    if not set(source_evidence).issubset(SOURCE_EVIDENCE_FIELDS):
        return None

    source_id = _clean(source_evidence.get("source_id"))
    if not source_id:
        return None

    normalized: dict[str, Any] = {"source_id": source_id}
    for field in ("source_type", "source_status", "semantic_status"):
        if field not in source_evidence:
            continue
        value = source_evidence.get(field)
        if value is not None and not isinstance(value, str):
            return None
        normalized[field] = _clean(value) or None

    matched_rules = source_evidence.get("matched_rules")
    if matched_rules is not None:
        if not isinstance(matched_rules, (list, tuple)):
            return None
        cleaned_rules = [_clean(rule) for rule in matched_rules]
        if any(not rule for rule in cleaned_rules):
            return None
        normalized["matched_rules"] = cleaned_rules

    return normalized
