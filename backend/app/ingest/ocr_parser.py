from __future__ import annotations

import re
from typing import Any


FIELD_ALIASES = {
    "order_id": [
        "order id",
        "order_id",
        "id ordine",
        "ordine",
        "n ordine",
        "nr ordine",
    ],
    "cliente": ["cliente", "customer", "ragione sociale"],
    "codice": ["codice", "code", "articolo", "cod articolo", "item code"],
    "qta": ["qta", "qtà", "q.ta", "quantita", "quantità", "qty"],
    "due_date": [
        "due date",
        "data richiesta",
        "data richiesta cliente",
        "consegna",
        "scadenza",
        "data consegna",
    ],
    "priority": ["priority", "priorita", "priorità", "urgenza", "prio"],
    "postazione": ["postazione", "linea", "reparto", "stazione", "workstation"],
    "note": ["note", "annotazioni", "commento", "commenti"],
}

PRIORITY_NORMALIZATION = {
    "urgent": "ALTA",
    "urgente": "ALTA",
    "alta": "ALTA",
    "high": "ALTA",
    "media": "MEDIA",
    "medium": "MEDIA",
    "normale": "MEDIA",
    "bassa": "BASSA",
    "low": "BASSA",
    "critica": "CRITICA",
    "critical": "CRITICA",
}


def parse_ocr_order_rows(
    rows: list[str] | list[dict[str, Any]] | str,
    *,
    source_type: str = "ocr_rows",
    source_file: str | None = None,
) -> dict[str, Any]:
    lines = _coerce_lines(rows)
    parsed: dict[str, Any] = {
        "order_id": "",
        "cliente": "",
        "codice": "",
        "qta": "",
        "due_date": "",
        "priority": "",
        "postazione": "",
        "note": "",
        "source_type": source_type,
        "source_file": source_file or "",
    }

    traces: list[dict[str, str]] = []
    unmatched_lines: list[str] = []

    for line in lines:
        normalized_line = _normalize_line(line)
        if not normalized_line:
            continue

        matched = False
        # 1) Prova a estrarre con alias ancorati a inizio riga
        for field_name in FIELD_ALIASES:
            value = _extract_alias_value(normalized_line, field_name)
            if value is None:
                continue
            parsed[field_name] = _normalize_field_value(field_name, value)
            traces.append({"field": field_name, "value": parsed[field_name], "source_line": normalized_line})
            matched = True
            break

        # 2) Se nessun alias ha matchato, prova euristiche sicure
        if not matched:
            # Euristica per order_id: applica solo su righe senza altri alias riconosciuti
            oid = _extract_fallback_value(normalized_line, "order_id")
            if oid:
                parsed["order_id"] = _normalize_field_value("order_id", oid)
                traces.append({"field": "order_id", "value": parsed["order_id"], "source_line": normalized_line})
                matched = True

        if not matched:
            due = _extract_fallback_value(normalized_line, "due_date")
            if due:
                parsed["due_date"] = _normalize_field_value("due_date", due)
                traces.append({"field": "due_date", "value": parsed["due_date"], "source_line": normalized_line})
                matched = True

        if not matched:
            q = _extract_fallback_value(normalized_line, "qta")
            if q:
                parsed["qta"] = _normalize_field_value("qta", q)
                traces.append({"field": "qta", "value": parsed["qta"], "source_line": normalized_line})
                matched = True

        if not matched:
            unmatched_lines.append(normalized_line)

    if unmatched_lines:
        existing_note = str(parsed.get("note", "") or "").strip()
        extra_note = " | ".join(unmatched_lines)
        parsed["note"] = (
            f"{existing_note} | OCR_EXTRA={extra_note}"
            if existing_note else f"OCR_EXTRA={extra_note}"
        )

    return {
        "parsed_order": parsed,
        "matched_fields": traces,
        "unmatched_lines": unmatched_lines,
        "input_rows_count": len(lines),
    }


def _coerce_lines(rows: list[str] | list[dict[str, Any]] | str) -> list[str]:
    if isinstance(rows, str):
        return [line.strip() for line in rows.splitlines() if line.strip()]

    lines: list[str] = []
    for item in rows:
        if isinstance(item, dict):
            line = " | ".join(
                str(value).strip()
                for value in item.values()
                if str(value).strip()
            )
            if line:
                lines.append(line)
            continue

        line = str(item).strip()
        if line:
            lines.append(line)

    return lines


def _normalize_line(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def _extract_alias_value(line: str, field_name: str) -> str | None:
    # Gestione robusta per quantità: supporta Q.tà, Q.ta, Qta, Quantità, Quantita, Qty
    if field_name == "qta":
        pattern_qta = re.compile(
            r"^\s*(?:q\s*\.?\s*t[aà]|qt[aà]|quantit[aà]|qty)\s*[:=\-]?\s*(.+)$",
            re.IGNORECASE,
        )
        m = pattern_qta.search(line)
        if m:
            return m.group(1).strip()

    aliases = FIELD_ALIASES[field_name]
    # match solo se l'alias è a inizio riga (dopo spazi)
    # prova prima gli alias più lunghi per evitare match parziali (es. "data richiesta" vs "data richiesta cliente")
    for alias in sorted(aliases, key=len, reverse=True):
        pattern = re.compile(rf"^\s*{re.escape(alias)}\s*[:=\-]?\s*(.+)$", re.IGNORECASE)
        match = pattern.search(line)
        if match:
            return match.group(1).strip()
    return None


def _extract_fallback_value(line: str, field_name: str) -> str | None:
    lowered = line.lower()
    if field_name == "order_id":
        # Evita di triggerare su righe che chiaramente indicano altri campi come codice o cliente
        other_keys = FIELD_ALIASES["codice"] + FIELD_ALIASES["cliente"] + FIELD_ALIASES["qta"]
        if any(k.lower() in lowered for k in other_keys):
            return None
        match = re.search(r"\b[A-Z]{2,}(?:[-_/][A-Z0-9]+)+\b", line, re.IGNORECASE)
        if match:
            return match.group(0)

    if field_name == "due_date":
        match = re.search(r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|\b\d{2}/\d{2}/\d{4}\b", line)
        if match:
            return match.group(0)

    if field_name == "qta":
        if any(a.lower() in lowered for a in FIELD_ALIASES["qta"]):
            match = re.search(r"(-?\d+(?:[.,]\d+)?)", line)
            if match:
                return match.group(1)
    return None


def _normalize_field_value(field_name: str, value: str) -> str:
    cleaned = str(value).strip().strip("|")

    if field_name == "priority":
        return PRIORITY_NORMALIZATION.get(cleaned.lower(), cleaned.upper())

    if field_name == "qta":
        return cleaned.replace(" ", "")

    if field_name == "due_date":
        return cleaned.replace("/", "-") if re.match(r"^\d{4}/\d{2}/\d{2}$", cleaned) else cleaned

    return cleaned
