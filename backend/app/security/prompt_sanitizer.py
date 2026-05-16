from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .data_boundary_classifier import classify_data_boundary


_LOCAL_PATH_PATTERN = re.compile(
    r"(?i)(?:/" "Users" r"/|/home/|[A-Z]:\\)[^\s'\"<>]+"
)
_EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+" "@" r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)
_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)(postgresql|postgres|mysql|mongodb)://(?!localhost/|127\.0\.0\.1/)[^\s'\"<>]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)DATABASE_URL\s*=\s*[^\s]+"),
)
_ARTICLE_PATTERN = re.compile(r"\b\d{5}[A-Z]{0,3}\b")
_COMPONENT_PATTERN = re.compile(r"\b\d{6}\b")


@dataclass(frozen=True)
class PromptSanitizationResult:
    sanitized_prompt: str
    sanitized: bool
    redaction_report: dict[str, Any]
    boundary_check: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sanitize_prompt(raw_prompt: str | None, *, scope_declared: bool = False) -> dict[str, Any]:
    prompt = str(raw_prompt or "")
    sanitized = prompt
    redactions: dict[str, int] = {
        "local_paths": 0,
        "emails": 0,
        "secrets": 0,
        "article_codes": 0,
        "component_codes": 0,
    }

    sanitized, redactions["local_paths"] = _sub_count(
        _LOCAL_PATH_PATTERN,
        "[LOCAL_PATH_REDACTED]",
        sanitized,
    )
    sanitized, redactions["emails"] = _sub_count(
        _EMAIL_PATTERN,
        "[EMAIL_REDACTED]",
        sanitized,
    )
    for pattern in _SECRET_PATTERNS:
        sanitized, count = _sub_count(pattern, "[SECRET_REDACTED]", sanitized)
        redactions["secrets"] += count

    sanitized, redactions["article_codes"] = _replace_codes(
        _ARTICLE_PATTERN,
        "ARTICLE",
        sanitized,
    )
    sanitized, redactions["component_codes"] = _replace_codes(
        _COMPONENT_PATTERN,
        "COMPONENT",
        sanitized,
    )

    boundary_check = classify_data_boundary(sanitized, scope_declared=scope_declared)

    return PromptSanitizationResult(
        sanitized_prompt=sanitized,
        sanitized=any(redactions.values()),
        redaction_report=redactions,
        boundary_check=boundary_check,
    ).to_dict()


def _sub_count(pattern: re.Pattern[str], repl: str, text: str) -> tuple[str, int]:
    count = 0

    def replace(_match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return repl

    return pattern.sub(replace, text), count


def _replace_codes(pattern: re.Pattern[str], prefix: str, text: str) -> tuple[str, int]:
    mapping: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        raw = match.group(0)
        if raw not in mapping:
            mapping[raw] = f"{prefix}_{chr(65 + len(mapping))}"
        return mapping[raw]

    updated = pattern.sub(replace, text)
    return updated, len(mapping)
