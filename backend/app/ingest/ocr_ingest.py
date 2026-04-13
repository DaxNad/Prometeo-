from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from ..smf.smf_adapter import SMFAdapter


ESSENTIAL_FIELDS = ("order_id", "codice", "qta")
TARGET_SHEET = "Pianificazione"
DISCREPANCY_SHEET = "DiscrepanzeLog"


class ExtractedOrderIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    order_id: str | None = None
    cliente: str | None = None
    codice: str | None = None
    qta: float | int | str | None = None
    due_date: str | None = None
    priority: str | None = None
    postazione: str | None = None
    note: str | None = None
    source_file: str | None = None
    source_type: str | None = None


@dataclass
class DiscrepancyItem:
    field: str
    expected: str
    found: str
    action: str
    outcome: str


def normalize_extracted_order(payload: ExtractedOrderIn | dict[str, Any]) -> dict[str, Any]:
    coerced_payload = _coerce_extracted_order_payload(payload)
    model = (
        coerced_payload
        if isinstance(coerced_payload, ExtractedOrderIn)
        else ExtractedOrderIn(**coerced_payload)
    )

    discrepancies: list[DiscrepancyItem] = []

    order_id = _clean_text(model.order_id)
    cliente = _clean_text(model.cliente)
    codice = _clean_text(model.codice)
    postazione = _clean_text(model.postazione)
    note = _clean_text(model.note)
    source_file = _clean_text(model.source_file)
    source_type = _clean_text(model.source_type) or "json_extracted"

    qta = _normalize_quantity(model.qta, discrepancies)
    due_date = _normalize_due_date(model.due_date, discrepancies)
    priority = _normalize_priority(model.priority, discrepancies)

    if not order_id:
        discrepancies.append(
            DiscrepancyItem(
                field="order_id",
                expected="valore non vuoto",
                found="",
                action="scrittura_con_id_vuoto",
                outcome="warning",
            )
        )
    if not codice:
        discrepancies.append(
            DiscrepancyItem(
                field="codice",
                expected="valore non vuoto",
                found="",
                action="scrittura_parziale",
                outcome="warning",
            )
        )
    if qta is None:
        discrepancies.append(
            DiscrepancyItem(
                field="qta",
                expected="numero valido",
                found=_clean_text(model.qta),
                action="default_zero",
                outcome="warning",
            )
        )

    source_type_lower = source_type.lower()
    if not postazione and not source_type_lower.startswith("ocr"):
        discrepancies.append(
            DiscrepancyItem(
                field="postazione",
                expected="valore non vuoto",
                found="",
                action="campo_vuoto",
                outcome="warning",
            )
        )

    semaforo = _semaforo_from_due(due_date)

    planning_row = {
        "ID ordine": order_id,
        "Cliente": cliente,
        "Codice": codice,
        "Q.ta": qta if qta is not None else 0,
        "Data richiesta cliente": due_date,
        "Priorità": priority,
        "Postazione assegnata": postazione,
        "Stato (da fare/in corso/finito)": "da fare",
        "Progress %": 0,
        "Semaforo scadenza": semaforo,
        "Note": _compose_note(note=note, source_file=source_file, source_type=source_type),
    }

    has_meaningful_payload = any(
        [
            planning_row["ID ordine"],
            planning_row["Cliente"],
            planning_row["Codice"],
            planning_row["Q.ta"],
            planning_row["Data richiesta cliente"],
            planning_row["Postazione assegnata"],
            note,
        ]
    )

    return {
        "normalized": {
            "order_id": order_id,
            "cliente": cliente,
            "codice": codice,
            "qta": planning_row["Q.ta"],
            "due_date": due_date,
            "priority": priority,
            "postazione": postazione,
            "note": note,
            "source_file": source_file,
            "source_type": source_type,
            "planning_row": planning_row,
        },
        "discrepancies": [_discrepancy_to_dict(item) for item in discrepancies],
        "has_meaningful_payload": has_meaningful_payload,
    }


def write_extracted_order_to_smf(
    payload: ExtractedOrderIn | dict[str, Any],
    *,
    adapter: SMFAdapter | None = None,
) -> dict[str, Any]:
    smf_adapter = adapter or SMFAdapter()
    normalized_payload = normalize_extracted_order(payload)
    normalized = normalized_payload["normalized"]
    discrepancies = list(normalized_payload["discrepancies"])
    code_validation = _validate_code_against_smf(normalized, smf_adapter, discrepancies)
    station_validation = _validate_station_against_smf(normalized, smf_adapter, discrepancies)

    if not smf_adapter.available():
        return {
            "ok": False,
            "error": "smf_unavailable",
            "write_mode": "smf_unavailable",
            "path": str(smf_adapter.master_path()),
            "target_sheet": TARGET_SHEET,
            "discrepancy_sheet": DISCREPANCY_SHEET,
            "normalized": normalized,
            "code_validation": code_validation,
            "station_validation": station_validation,
            "discrepancies": discrepancies,
            "smf_write": {"ok": False, "mode": "smf_unavailable"},
            "debug": _build_debug_payload(
                normalized=normalized,
                code_validation=code_validation,
                station_validation=station_validation,
                discrepancies=discrepancies,
                smf_write={"ok": False, "mode": "smf_unavailable"},
                path=str(smf_adapter.master_path()),
            ),
        }

    if not normalized_payload["has_meaningful_payload"]:
        discrepancies.append(
            _discrepancy_to_dict(
                DiscrepancyItem(
                    field="payload",
                    expected="almeno un campo utile",
                    found="payload vuoto",
                    action="skip_scrittura",
                    outcome="warning",
                )
            )
        )
        discrepancy_log = _write_discrepancies(smf_adapter, normalized, discrepancies)
        return {
            "ok": True,
            "write_mode": "skipped_empty_payload",
            "normalized": normalized,
            "code_validation": code_validation,
            "station_validation": station_validation,
            "discrepancies": discrepancies,
            "smf_write": {"ok": False, "mode": "skipped_empty_payload"},
            "discrepancy_log": discrepancy_log,
            "path": str(smf_adapter.master_path()),
            "target_sheet": TARGET_SHEET,
            "discrepancy_sheet": DISCREPANCY_SHEET,
            "debug": _build_debug_payload(
                normalized=normalized,
                code_validation=code_validation,
                station_validation=station_validation,
                discrepancies=discrepancies,
                smf_write={"ok": False, "mode": "skipped_empty_payload"},
                path=str(smf_adapter.master_path()),
            ),
        }

    order_id = normalized["order_id"]
    planning_row = normalized["planning_row"]
    mutable_updates = {
        key: value
        for key, value in planning_row.items()
        if key != "ID ordine"
    }

    write_result: dict[str, Any]
    if order_id:
        update_result = smf_adapter.update_order(order_id, mutable_updates)
        if update_result.get("ok") is True:
            write_result = {
                "mode": "update_order",
                "result_type": "update_order_succeeded",
                **update_result,
            }
        else:
            discrepancies.append(
                _discrepancy_to_dict(
                    DiscrepancyItem(
                        field="order_id",
                        expected="riga esistente in Pianificazione",
                        found=order_id,
                        action="fallback_append_order",
                        outcome="warning",
                    )
                )
            )
            append_result = smf_adapter.append_order(planning_row)
            write_result = {
                "mode": "append_order",
                "result_type": "update_not_found_fallback_append",
                "fallback_from": {
                    "mode": "update_order",
                    "matched_column": update_result.get("matched_column"),
                    "written_columns": update_result.get("written_columns", []),
                    "error": update_result.get("error", "row not found"),
                },
                **append_result,
            }
    else:
        append_result = smf_adapter.append_order(planning_row)
        write_result = {
            "mode": "append_order",
            "result_type": "append_without_order_id",
            **append_result,
        }

    discrepancy_log = _write_discrepancies(smf_adapter, normalized, discrepancies)

    return {
        "ok": bool(write_result.get("ok")),
        "write_mode": str(write_result.get("mode", "")),
        "normalized": normalized,
        "code_validation": code_validation,
        "station_validation": station_validation,
        "discrepancies": discrepancies,
        "smf_write": write_result,
        "discrepancy_log": discrepancy_log,
        "path": str(smf_adapter.master_path()),
        "target_sheet": TARGET_SHEET,
        "discrepancy_sheet": DISCREPANCY_SHEET,
        "debug": _build_debug_payload(
            normalized=normalized,
            code_validation=code_validation,
            station_validation=station_validation,
            discrepancies=discrepancies,
            smf_write=write_result,
            path=str(smf_adapter.master_path()),
        ),
    }


def write_extracted_orders_to_smf(
    payloads: list[ExtractedOrderIn | dict[str, Any]],
    *,
    adapter: SMFAdapter | None = None,
) -> dict[str, Any]:
    smf_adapter = adapter or SMFAdapter()
    items: list[dict[str, Any]] = []

    summary = {
        "total": len(payloads),
        "written": 0,
        "updated": 0,
        "appended": 0,
        "duplicates": 0,
        "warnings": 0,
        "errors": 0,
    }
    seen_order_ids: set[str] = set()

    for index, payload in enumerate(payloads, start=1):
        normalized_preview = normalize_extracted_order(payload)
        order_id = str(normalized_preview.get("normalized", {}).get("order_id", "") or "").strip().upper()
        if order_id and order_id in seen_order_ids:
            result = _build_duplicate_skip_result(payload, smf_adapter)
            summary["duplicates"] += 1
        else:
            if order_id:
                seen_order_ids.add(order_id)
            result = write_extracted_order_to_smf(payload, adapter=smf_adapter)
        item = {"index": index, **result}
        items.append(item)

        if result.get("smf_write", {}).get("ok") is True:
            summary["written"] += 1

        result_type = str(result.get("smf_write", {}).get("result_type", "") or "")
        if result_type == "update_order_succeeded":
            summary["updated"] += 1
        elif result_type in {"update_not_found_fallback_append", "append_without_order_id"}:
            summary["appended"] += 1

        discrepancies_count = len(result.get("discrepancies", []))
        if discrepancies_count > 0:
            summary["warnings"] += discrepancies_count

        if not result.get("ok"):
            summary["errors"] += 1

    return {
        "ok": summary["errors"] == 0,
        "summary": summary,
        "items": items,
        "target_sheet": TARGET_SHEET,
        "discrepancy_sheet": DISCREPANCY_SHEET,
        "path": str(smf_adapter.master_path()),
    }


def _write_discrepancies(
    adapter: SMFAdapter,
    normalized: dict[str, Any],
    discrepancies: list[dict[str, Any]],
) -> dict[str, Any]:
    if not discrepancies:
        return {"ok": True, "rows": 0}

    writer = adapter.writer()
    written = 0
    errors: list[str] = []

    for item in discrepancies:
        result = writer.append_row(
            DISCREPANCY_SHEET,
            {
                "Timestamp": datetime.now().isoformat(timespec="seconds"),
                "Sorgente": _build_source_label(
                    normalized.get("source_type", ""),
                    normalized.get("source_file", ""),
                ),
                "Voce": item["field"],
                "Valore atteso": item["expected"],
                "Valore trovato": item["found"],
                "Azione eseguita": item["action"],
                "Esito": item["outcome"],
            },
        )
        if result.get("ok"):
            written += 1
        else:
            errors.append(str(result))

    return {"ok": len(errors) == 0, "rows": written, "errors": errors}


def _normalize_quantity(value: Any, discrepancies: list[DiscrepancyItem]) -> float | None:
    if value is None or str(value).strip() == "":
        return None

    raw = str(value).strip().replace(",", ".")
    try:
        parsed = float(raw)
    except ValueError:
        discrepancies.append(
            DiscrepancyItem(
                field="qta",
                expected="numero valido",
                found=str(value),
                action="default_zero",
                outcome="warning",
            )
        )
        return None

    if parsed < 0:
        discrepancies.append(
            DiscrepancyItem(
                field="qta",
                expected="numero >= 0",
                found=str(value),
                action="default_zero",
                outcome="warning",
            )
        )
        return None

    return int(parsed) if parsed.is_integer() else parsed


def _normalize_due_date(value: Any, discrepancies: list[DiscrepancyItem]) -> str:
    raw = _clean_text(value)
    if not raw:
        return ""

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            iso = datetime.strptime(raw, fmt).date().isoformat()
            if fmt != "%Y-%m-%d":
                discrepancies.append(
                    DiscrepancyItem(
                        field="due_date",
                        expected="data ISO (YYYY-MM-DD)",
                        found=raw,
                        action="normalized_date_to_iso",
                        outcome="warning",
                    )
                )
            return iso
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw).date().isoformat()
    except ValueError:
        discrepancies.append(
            DiscrepancyItem(
                field="due_date",
                expected="data ISO o gg/mm/aaaa",
                found=raw,
                action="campo_vuoto",
                outcome="warning",
            )
        )
        return ""


def _normalize_priority(value: Any, discrepancies: list[DiscrepancyItem]) -> str:
    raw = _clean_text(value).upper()
    if not raw:
        return "MEDIA"

    aliases = {
        "URGENT": "ALTA",
        "URGENTE": "ALTA",
        "HIGH": "ALTA",
        "MEDIUM": "MEDIA",
        "LOW": "BASSA",
        "NORMAL": "MEDIA",
        "NORMALE": "MEDIA",
        "CRITICAL": "CRITICA",
    }
    mapped = aliases.get(raw, raw)
    if mapped != raw:
        discrepancies.append(
            DiscrepancyItem(
                field="priority",
                expected="CRITICA|ALTA|MEDIA|BASSA",
                found=raw,
                action=f"normalized_priority_to_{mapped}",
                outcome="warning",
            )
        )
    raw = mapped

    allowed = {"CRITICA", "ALTA", "MEDIA", "BASSA"}
    if raw in allowed:
        return raw

    discrepancies.append(
        DiscrepancyItem(
            field="priority",
            expected="CRITICA|ALTA|MEDIA|BASSA",
            found=raw,
            action="default_MEDIA",
            outcome="warning",
        )
    )
    return "MEDIA"


def _semaforo_from_due(due_date: str) -> str:
    if not due_date:
        return "GIALLO"
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        return "GIALLO"

    delta = (due - date.today()).days
    if delta < 0:
        return "ROSSO"
    if delta <= 1:
        return "GIALLO"
    return "VERDE"


def _compose_note(*, note: str, source_file: str, source_type: str) -> str:
    parts = [part for part in [note] if part]
    source_parts = [part for part in [source_type, source_file] if part]
    if source_parts:
        parts.append("origine=" + "|".join(source_parts))
    return " | ".join(parts)


def _build_source_label(source_type: str, source_file: str) -> str:
    parts = [part for part in [source_type, source_file] if part]
    return " / ".join(parts) if parts else "json_extracted"


def _build_debug_payload(
    *,
    normalized: dict[str, Any],
    code_validation: dict[str, Any],
    station_validation: dict[str, Any],
    discrepancies: list[dict[str, Any]],
    smf_write: dict[str, Any],
    path: str,
) -> dict[str, Any]:
    planning_row = dict(normalized.get("planning_row", {}))
    return {
        "target_path": path,
        "target_sheet": TARGET_SHEET,
        "discrepancy_sheet": DISCREPANCY_SHEET,
        "order_id": normalized.get("order_id", ""),
        "source_type": normalized.get("source_type", ""),
        "source_file": normalized.get("source_file", ""),
        "code_validation": code_validation,
        "station_validation": station_validation,
        "planning_row_preview": planning_row,
        "requested_columns": smf_write.get("requested_columns", []),
        "written_columns": smf_write.get("written_columns", []),
        "matched_column": smf_write.get("matched_column"),
        "result_type": smf_write.get("result_type", ""),
        "write_decision": {
            "result_type": smf_write.get("result_type", ""),
            "code_validation_status": code_validation.get("status", ""),
            "station_validation_status": station_validation.get("status", ""),
        },
        "discrepancy_count": len(discrepancies),
    }


def _validate_code_against_smf(
    normalized: dict[str, Any],
    adapter: SMFAdapter,
    discrepancies: list[dict[str, Any]],
) -> dict[str, Any]:
    codice = str(normalized.get("codice", "") or "").strip()
    if not codice:
        return {
            "status": "missing",
            "found": False,
            "sheet": "Codici",
            "column": "Codice",
            "code": codice,
        }

    result = adapter.reader().code_exists(codice)
    status = "found" if result.get("found") else "missing"
    code_validation = {
        "status": status,
        "found": bool(result.get("found")),
        "sheet": result.get("sheet", "Codici"),
        "column": result.get("column", "Codice"),
        "matched_column": result.get("matched_column"),
        "code": result.get("code", codice),
    }
    if result.get("error"):
        code_validation["error"] = result["error"]

    if status == "missing":
        discrepancies.append(
            _discrepancy_to_dict(
                DiscrepancyItem(
                    field="codice",
                    expected="codice presente nel foglio Codici",
                    found=codice,
                    action="scrittura_con_warning_codice_non_censito",
                    outcome="warning",
                )
            )
        )

    return code_validation


def _validate_station_against_smf(
    normalized: dict[str, Any],
    adapter: SMFAdapter,
    discrepancies: list[dict[str, Any]],
) -> dict[str, Any]:
    postazione = str(normalized.get("postazione", "") or "").strip()
    if not postazione:
        return {
            "status": "missing",
            "found": False,
            "sheet": "Postazioni",
            "column": "Postazione",
            "matched_column": None,
            "station": postazione,
        }

    result = adapter.reader().station_exists(postazione)
    status = "found" if result.get("found") else "missing"
    station_validation = {
        "status": status,
        "found": bool(result.get("found")),
        "sheet": result.get("sheet", "Postazioni"),
        "column": result.get("column", "Postazione"),
        "matched_column": result.get("matched_column"),
        "station": result.get("station", postazione),
    }
    if result.get("error"):
        station_validation["error"] = result["error"]

    if status == "missing":
        discrepancies.append(
            _discrepancy_to_dict(
                DiscrepancyItem(
                    field="postazione",
                    expected="postazione presente nel foglio Postazioni",
                    found=postazione,
                    action="scrittura_con_warning_postazione_non_censita",
                    outcome="warning",
                )
            )
        )

    return station_validation


def _coerce_extracted_order_payload(
    payload: ExtractedOrderIn | dict[str, Any],
) -> ExtractedOrderIn | dict[str, Any]:
    if isinstance(payload, ExtractedOrderIn):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("parsed_order"), dict):
        return payload["parsed_order"]
    return payload


def _build_duplicate_skip_result(
    payload: ExtractedOrderIn | dict[str, Any],
    adapter: SMFAdapter,
) -> dict[str, Any]:
    normalized_payload = normalize_extracted_order(payload)
    normalized = normalized_payload["normalized"]
    discrepancies = list(normalized_payload["discrepancies"])
    discrepancies.append(
        _discrepancy_to_dict(
            DiscrepancyItem(
                field="order_id",
                expected="order_id univoco nel batch",
                found=str(normalized.get("order_id", "")),
                action="skip_duplicate_batch_item",
                outcome="warning",
            )
        )
    )
    code_validation = _validate_code_against_smf(normalized, adapter, discrepancies)
    station_validation = _validate_station_against_smf(normalized, adapter, discrepancies)
    discrepancy_log = _write_discrepancies(adapter, normalized, discrepancies)
    smf_write = {
        "ok": False,
        "mode": "skipped_duplicate_order_id",
        "result_type": "duplicate_order_id_skipped",
        "matched_column": None,
        "requested_columns": [],
        "written_columns": [],
    }
    return {
        "ok": True,
        "write_mode": "skipped_duplicate_order_id",
        "normalized": normalized,
        "code_validation": code_validation,
        "station_validation": station_validation,
        "discrepancies": discrepancies,
        "smf_write": smf_write,
        "discrepancy_log": discrepancy_log,
        "path": str(adapter.master_path()),
        "target_sheet": TARGET_SHEET,
        "discrepancy_sheet": DISCREPANCY_SHEET,
        "debug": _build_debug_payload(
            normalized=normalized,
            code_validation=code_validation,
            station_validation=station_validation,
            discrepancies=discrepancies,
            smf_write=smf_write,
            path=str(adapter.master_path()),
        ),
    }


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _discrepancy_to_dict(item: DiscrepancyItem) -> dict[str, str]:
    return {
        "field": item.field,
        "expected": item.expected,
        "found": item.found,
        "action": item.action,
        "outcome": item.outcome,
    }
