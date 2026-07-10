from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any


ERROR_INVALID_INPUT = "INVALID_INPUT"
ERROR_MISSING_SOURCE_ID = "MISSING_SOURCE_ID"
ERROR_EMPTY_INPUT = "EMPTY_INPUT"
ERROR_NO_RECOGNIZED_FIELDS = "NO_RECOGNIZED_FIELDS"

SOURCE_TYPE = "photographed_article_spec_text"
SOURCE_STATUS = "SOURCE_FOUND"
FIELD_STATUS = "DA_VERIFICARE"
PARSER_CAPABILITY = "ARTICLE_SPECIFICATION_TEXT_PARSER_V1"
ROUTE_EVIDENCE = "UNCONFIRMED_EXTRACTED_TEXT"

LABELED_FIELDS = (
    ("revision_date", ("REV DATA", "DATA REVISIONE", "REVISION DATE")),
    ("customer_code", ("CODICE", "CODICE CLIENTE", "CUSTOMER CODE")),
    ("article", ("ARTICOLO", "ARTICLE", "CODICE ARTICOLO")),
    ("drawing", ("DISEGNO", "DRAWING")),
    ("revision", ("REV", "REVISIONE", "REVISION")),
    ("description", ("DESCRIZIONE", "DESCRIPTION")),
    ("material", ("MATERIALE", "MATERIAL")),
)

SECTION_FIELDS = {
    "OPERAZIONI": "operation",
    "OPERATIONS": "operation",
    "CICLO": "operation",
    "FASI": "operation",
    "COMPONENTI": "component_code",
    "COMPONENTS": "component_code",
    "DISTINTA": "component_code",
    "BOM": "component_code",
    "ATTREZZATURE": "tool",
    "TOOLS": "tool",
    "TOOLING": "tool",
    "COLLAUDI": "quality_control",
    "CONTROLLI": "quality_control",
    "QUALITY CONTROLS": "quality_control",
    "VINCOLI": "constraint",
    "CONSTRAINTS": "constraint",
}


class ArticleSpecificationParseStatus(str, Enum):
    PARSED = "PARSED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ArticleSpecificationParseResult:
    ok: bool
    status: ArticleSpecificationParseStatus
    source_id: str
    payloads: tuple[dict[str, Any], ...]
    unmatched_lines: tuple[str, ...]
    error_code: str | None = None


def parse_article_specification_rows(
    rows: Sequence[str] | str,
    *,
    source_id: str,
) -> ArticleSpecificationParseResult:
    normalized_source_id = _clean(source_id)
    if not normalized_source_id:
        return _rejected(ERROR_MISSING_SOURCE_ID)

    lines = _coerce_lines(rows)
    if lines is None:
        return _rejected(ERROR_INVALID_INPUT, source_id=normalized_source_id)
    if not lines:
        return _rejected(ERROR_EMPTY_INPUT, source_id=normalized_source_id)

    article = _find_article(lines)
    payloads: list[dict[str, Any]] = []
    unmatched_lines: list[str] = []
    current_section: str | None = None
    operation_sequence = 0

    for line_number, source_line in lines:
        section = _section_name(source_line)
        if section is not None:
            current_section = section
            continue

        labeled_field = _extract_labeled_field(source_line)
        if labeled_field is not None:
            field_name, value = labeled_field
            payloads.append(
                _build_payload(
                    field_name=field_name,
                    value=value,
                    source_id=normalized_source_id,
                    source_line=source_line,
                    line_number=line_number,
                    article=article,
                    document_section="ARTICOLO",
                )
            )
            continue

        field_name = SECTION_FIELDS.get(current_section or "")
        if field_name is None:
            unmatched_lines.append(source_line)
            continue

        value, detail = _section_value(field_name, source_line)
        if not value:
            unmatched_lines.append(source_line)
            continue

        if field_name == "operation":
            operation_sequence += 1

        payloads.append(
            _build_payload(
                field_name=field_name,
                value=value,
                source_id=normalized_source_id,
                source_line=source_line,
                line_number=line_number,
                article=article,
                document_section=current_section,
                detail=detail,
                operation_sequence=operation_sequence if field_name == "operation" else None,
            )
        )

    if not payloads:
        return ArticleSpecificationParseResult(
            ok=False,
            status=ArticleSpecificationParseStatus.REJECTED,
            source_id=normalized_source_id,
            payloads=(),
            unmatched_lines=tuple(unmatched_lines),
            error_code=ERROR_NO_RECOGNIZED_FIELDS,
        )

    return ArticleSpecificationParseResult(
        ok=True,
        status=ArticleSpecificationParseStatus.PARSED,
        source_id=normalized_source_id,
        payloads=tuple(payloads),
        unmatched_lines=tuple(unmatched_lines),
    )


def _coerce_lines(rows: Sequence[str] | str) -> list[tuple[int, str]] | None:
    if isinstance(rows, str):
        raw_lines: Sequence[Any] = rows.splitlines()
    elif isinstance(rows, Sequence) and not isinstance(rows, (bytes, bytearray)):
        raw_lines = rows
    else:
        return None

    if any(not isinstance(row, str) for row in raw_lines):
        return None

    return [
        (line_number, cleaned)
        for line_number, row in enumerate(raw_lines, start=1)
        if (cleaned := _clean(row))
    ]


def _find_article(lines: list[tuple[int, str]]) -> str:
    for _line_number, source_line in lines:
        labeled_field = _extract_labeled_field(source_line)
        if labeled_field is not None and labeled_field[0] == "article":
            return labeled_field[1]
    return ""


def _extract_labeled_field(line: str) -> tuple[str, str] | None:
    for field_name, aliases in LABELED_FIELDS:
        for alias in sorted(aliases, key=len, reverse=True):
            match = re.fullmatch(
                rf"\s*{re.escape(alias)}\s*[:=\-]\s*(.+?)\s*",
                line,
                flags=re.IGNORECASE,
            )
            if match:
                value = _clean(match.group(1))
                return (field_name, value) if value else None
    return None


def _section_name(line: str) -> str | None:
    token = re.sub(r"\s+", " ", line.strip().rstrip(":")).upper()
    return token if token in SECTION_FIELDS else None


def _section_value(field_name: str, source_line: str) -> tuple[str, str]:
    if field_name not in {"component_code", "tool"}:
        return source_line, ""

    match = re.match(r"^([A-Z0-9][A-Z0-9._/-]*)\b(.*)$", source_line, flags=re.IGNORECASE)
    if not match:
        return "", ""
    return _clean(match.group(1)), _clean(match.group(2).lstrip(" :-"))


def _build_payload(
    *,
    field_name: str,
    value: str,
    source_id: str,
    source_line: str,
    line_number: int,
    article: str,
    document_section: str | None,
    detail: str = "",
    operation_sequence: int | None = None,
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    if article:
        context["article"] = article
    if field_name == "component_code":
        context["component_code"] = value
    if operation_sequence is not None:
        context["sequence"] = operation_sequence
        context["route_status"] = FIELD_STATUS

    metadata: dict[str, Any] = {
        "parser_capability": PARSER_CAPABILITY,
        "field_status": FIELD_STATUS,
        "source_line": source_line,
        "source_line_number": line_number,
    }
    if detail:
        metadata["source_detail"] = detail
    if operation_sequence is not None:
        metadata["route_evidence"] = ROUTE_EVIDENCE

    return {
        "field_name": field_name,
        "value": value,
        "source_id": source_id,
        "source_type": SOURCE_TYPE,
        "source_status": SOURCE_STATUS,
        "semantic_status": FIELD_STATUS,
        "document_section": document_section,
        "document_label": document_section,
        "context": context,
        "metadata": metadata,
    }


def _rejected(
    error_code: str,
    *,
    source_id: str = "",
) -> ArticleSpecificationParseResult:
    return ArticleSpecificationParseResult(
        ok=False,
        status=ArticleSpecificationParseStatus.REJECTED,
        source_id=source_id,
        payloads=(),
        unmatched_lines=(),
        error_code=error_code,
    )


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())
