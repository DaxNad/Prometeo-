from __future__ import annotations

from hashlib import sha256
import re
from typing import Any

from app.ingest.ocr_parser import parse_ocr_order_rows

CAPABILITY = "PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001"
SOURCE_TYPE = "structured_text"
SOURCE_FOUND = "SOURCE_FOUND"
SOURCE_REJECTED = "SOURCE_REJECTED"
DA_VERIFICARE = "DA_VERIFICARE"
INCOMPLETO = "INCOMPLETO"
BLOCCATO = "BLOCCATO"
RECORD_DELIMITER = "--- RECORD ---"
PERIOD_PREFIX = "PERIODO:"
REQUIRED_ROW_FIELDS = ("order_id", "article_code", "quantity")
CUSTOMER_REQUESTED_DATE_LABELS = {
    "data richiesta cliente",
    "customer requested date",
}
AMBIGUOUS_DATE_LABELS = {
    "data",
    "scadenza",
    "consegna",
    "due date",
    "data consegna",
}
DATE_LABELS = CUSTOMER_REQUESTED_DATE_LABELS | AMBIGUOUS_DATE_LABELS


def build_production_program_snapshot_preview(
    structured_text: str,
    *,
    source_id: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, read-only preview from structured text."""
    normalized_text = _normalize_input(structured_text)
    digest = sha256(normalized_text.encode("utf-8")).hexdigest()
    resolved_source_id = (
        source_id.strip()
        if isinstance(source_id, str) and source_id.strip()
        else f"production-program-text:sha256:{digest}"
    )
    snapshot_id = f"production-program-snapshot:sha256:{digest}"

    if not normalized_text:
        return _blocked(snapshot_id, resolved_source_id, None, "empty_input")

    period, records_text = _extract_period(normalized_text)
    blocks = _split_records(records_text)
    if blocks is None:
        return _blocked(
            snapshot_id,
            resolved_source_id,
            period,
            "record_delimiter_required",
        )

    orders: list[dict[str, Any]] = []
    missing_fields: list[dict[str, Any]] = []
    ambiguous_fields: list[dict[str, Any]] = []
    discrepancies: list[dict[str, Any]] = []

    for index, block in enumerate(blocks, start=1):
        order = _build_order(block, index=index, source_id=resolved_source_id)
        orders.append(order)
        missing_fields.extend(
            {"record_index": index, "field": field}
            for field in order["missing_fields"]
        )
        ambiguous_fields.extend(
            {"record_index": index, **item}
            for item in order["ambiguous_fields"]
        )
        discrepancies.extend(
            {"record_index": index, "code": code}
            for code in order["discrepancies"]
        )

    if period is None:
        missing_fields.append({"field": "period"})

    incomplete = bool(missing_fields)
    ambiguous = bool(ambiguous_fields)
    return {
        "ok": True,
        "capability": CAPABILITY,
        "snapshot_id": snapshot_id,
        "source_id": resolved_source_id,
        "source_type": SOURCE_TYPE,
        "source_status": SOURCE_FOUND,
        "period": period,
        "orders": orders,
        "missing_fields": missing_fields,
        "ambiguous_fields": ambiguous_fields,
        "discrepancies": discrepancies,
        "confidence": "LOW" if incomplete or ambiguous else "MEDIUM",
        "semantic_status": INCOMPLETO if incomplete else DA_VERIFICARE,
        "requires_confirmation": True,
        "persisted": False,
        "writer_called": False,
        "planner_called": False,
        "pattern_learning_called": False,
    }


def _blocked(
    snapshot_id: str,
    source_id: str,
    period: str | None,
    discrepancy: str,
) -> dict[str, Any]:
    return {
        "ok": False,
        "capability": CAPABILITY,
        "snapshot_id": snapshot_id,
        "source_id": source_id,
        "source_type": SOURCE_TYPE,
        "source_status": SOURCE_REJECTED,
        "period": period,
        "orders": [],
        "missing_fields": ["records"],
        "ambiguous_fields": [],
        "discrepancies": [discrepancy],
        "confidence": "LOW",
        "semantic_status": BLOCCATO,
        "requires_confirmation": True,
        "persisted": False,
        "writer_called": False,
        "planner_called": False,
        "pattern_learning_called": False,
    }


def _build_order(block: str, *, index: int, source_id: str) -> dict[str, Any]:
    parsed = parse_ocr_order_rows(
        block,
        source_type=SOURCE_TYPE,
        source_file=None,
    )
    parsed_order = parsed["parsed_order"]

    provenance: dict[str, dict[str, Any]] = {}
    for trace in parsed["matched_fields"]:
        field = _canonical_field(trace["field"])
        provenance[field] = {
            "source_id": source_id,
            "source_type": SOURCE_TYPE,
            "record_index": index,
            "source_line": trace["source_line"],
            "observed_field": trace["field"],
        }

    requested_date, requested_date_provenance, ambiguous_dates = _dates(
        block,
        source_id=source_id,
        index=index,
    )
    if requested_date_provenance is not None:
        provenance["customer_requested_date"] = requested_date_provenance

    quantity, quantity_error = _quantity(parsed_order.get("qta"))
    values = {
        "order_id": _clean(parsed_order.get("order_id")),
        "article_code": _clean(parsed_order.get("codice")),
        "quantity": quantity,
        "customer_requested_date": requested_date,
        "priority": _clean(parsed_order.get("priority")) or None,
        "station_hint": _clean(parsed_order.get("postazione")) or None,
    }
    missing = [
        field
        for field in REQUIRED_ROW_FIELDS
        if values[field] is None or values[field] == ""
    ]
    statuses = {
        field: INCOMPLETO if value is None or value == "" else DA_VERIFICARE
        for field, value in values.items()
    }

    return {
        **values,
        "record_index": index,
        "semantic_status": INCOMPLETO if missing else DA_VERIFICARE,
        "field_statuses": statuses,
        "field_provenance": provenance,
        "missing_fields": missing,
        "ambiguous_fields": ambiguous_dates,
        "discrepancies": [quantity_error] if quantity_error else [],
        "unmatched_content": list(parsed["unmatched_lines"]),
    }


def _extract_period(text: str) -> tuple[str | None, str]:
    period: str | None = None
    remaining: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if period is None and stripped.upper().startswith(PERIOD_PREFIX):
            period = stripped[len(PERIOD_PREFIX) :].strip() or None
            continue
        remaining.append(line)
    return period, "\n".join(remaining).strip()


def _split_records(text: str) -> list[str] | None:
    if RECORD_DELIMITER not in text:
        return None
    blocks = [block.strip() for block in text.split(RECORD_DELIMITER)]
    if len(blocks) < 2 or any(not block for block in blocks):
        return None
    return blocks


def _dates(
    block: str,
    *,
    source_id: str,
    index: int,
) -> tuple[str | None, dict[str, Any] | None, list[dict[str, Any]]]:
    requested: str | None = None
    requested_provenance: dict[str, Any] | None = None
    ambiguous: list[dict[str, Any]] = []

    for line in block.splitlines():
        normalized = re.sub(r"\s+", " ", line.strip())
        label, value = _labeled_date(normalized)
        if label is None:
            continue
        folded = label.casefold()
        if folded in CUSTOMER_REQUESTED_DATE_LABELS:
            requested = value
            requested_provenance = {
                "source_id": source_id,
                "source_type": SOURCE_TYPE,
                "record_index": index,
                "source_line": normalized,
                "observed_field": label,
            }
        elif folded in AMBIGUOUS_DATE_LABELS:
            ambiguous.append(
                {
                    "field": "date_meaning",
                    "raw_value": value,
                    "source_line": normalized,
                    "observed_label": label,
                }
            )

    return requested, requested_provenance, ambiguous


def _labeled_date(line: str) -> tuple[str | None, str]:
    separated = re.fullmatch(r"\s*([^:=\-]+?)\s*[:=\-]\s*(.+?)\s*", line)
    if separated:
        return separated.group(1).strip(), separated.group(2).strip()

    for label in sorted(DATE_LABELS, key=len, reverse=True):
        separatorless = re.fullmatch(
            rf"\s*({re.escape(label)})\s+(.+?)\s*",
            line,
            flags=re.IGNORECASE,
        )
        if separatorless:
            return separatorless.group(1).strip(), separatorless.group(2).strip()
    return None, ""


def _quantity(value: Any) -> tuple[int | float | None, str | None]:
    raw = _clean(value)
    if not raw:
        return None, None
    try:
        number = float(raw.replace(" ", "").replace(",", "."))
    except ValueError:
        return None, "quantity_not_numeric"
    if number <= 0:
        return None, "quantity_must_be_positive"
    return (int(number) if number.is_integer() else number), None


def _canonical_field(field: str) -> str:
    return {
        "codice": "article_code",
        "qta": "quantity",
        "due_date": "observed_date",
        "postazione": "station_hint",
    }.get(field, field)


def _normalize_input(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return "\n".join(line.rstrip() for line in value.strip().splitlines())


def _clean(value: Any) -> str:
    return str(value or "").strip()
