import asyncio

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from .ingest.ocr_ingest import (
    ExtractedOrderIn,
    normalize_extracted_order,
    write_extracted_order_to_smf,
    write_extracted_orders_to_smf,
)
from .ingest.ocr_parser import parse_ocr_order_rows
from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/smf", tags=["smf"])

adapter: SMFAdapter | None = None
agent_runtime = None


class ParseExtractedOrderRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    raw_text: str | None = None
    rows: list[str] | list[dict] | None = None
    order_id: str | None = None
    cliente: str | None = Field(default=None, validation_alias=AliasChoices("cliente", "customer"))
    codice: str | None = Field(default=None, validation_alias=AliasChoices("codice", "code"))
    qta: float | int | str | None = Field(default=None, validation_alias=AliasChoices("qta", "quantity"))
    postazione: str | None = Field(default=None, validation_alias=AliasChoices("postazione", "station"))
    due_date: str | None = Field(default=None, validation_alias=AliasChoices("due_date", "customer_due_date"))
    priority: str | None = None
    note: str | None = None
    source_file: str | None = None
    source_type: str | None = "ocr_raw"


def _build_structured_parse_result(payload: ParseExtractedOrderRequest) -> dict:
    parsed_order = {
        "order_id": str(payload.order_id or "").strip(),
        "cliente": str(payload.cliente or "").strip(),
        "codice": str(payload.codice or "").strip(),
        "qta": "" if payload.qta is None else str(payload.qta).strip(),
        "due_date": str(payload.due_date or "").strip(),
        "priority": str(payload.priority or "").strip(),
        "postazione": str(payload.postazione or "").strip(),
        "note": str(payload.note or "").strip(),
        "source_type": str(payload.source_type or "ocr_structured").strip(),
        "source_file": str(payload.source_file or "").strip(),
    }
    matched_fields = [
        {"field": key, "value": value, "source_line": "structured_payload"}
        for key, value in parsed_order.items()
        if key not in {"source_type", "source_file"} and str(value).strip()
    ]
    return {
        "parsed_order": parsed_order,
        "matched_fields": matched_fields,
        "unmatched_lines": [],
        "input_rows_count": len(matched_fields),
    }


def _build_parse_only_result(
    payload: ParseExtractedOrderRequest,
    *,
    smf_adapter: SMFAdapter,
) -> dict:
    raw_input = payload.rows if payload.rows is not None else (payload.raw_text or "")
    if raw_input:
        parsed = parse_ocr_order_rows(
            raw_input,
            source_type=payload.source_type or "ocr_raw",
            source_file=payload.source_file,
        )
    else:
        parsed = _build_structured_parse_result(payload)
    normalized_result = normalize_extracted_order(parsed)
    codice = normalized_result.get("normalized", {}).get("codice", "")
    code_check = smf_adapter.reader().code_exists(codice) if codice else {
        "ok": True,
        "found": False,
        "sheet": "Codici",
        "column": "Codice",
        "matched_column": None,
        "code": "",
    }
    postazione = normalized_result.get("normalized", {}).get("postazione", "")
    station_check = smf_adapter.reader().station_exists(postazione) if postazione else {
        "ok": True,
        "found": False,
        "sheet": "Postazioni",
        "column": "Postazione",
        "matched_column": None,
        "station": "",
    }
    code_validation = {
        "status": "found" if code_check.get("found") else "missing",
        "found": bool(code_check.get("found")),
        "sheet": code_check.get("sheet", "Codici"),
        "column": code_check.get("column", "Codice"),
        "matched_column": code_check.get("matched_column"),
        "code": code_check.get("code", codice),
    }
    if code_check.get("error"):
        code_validation["error"] = code_check["error"]

    station_validation = {
        "status": "found" if station_check.get("found") else "missing",
        "found": bool(station_check.get("found")),
        "sheet": station_check.get("sheet", "Postazioni"),
        "column": station_check.get("column", "Postazione"),
        "matched_column": station_check.get("matched_column"),
        "station": station_check.get("station", postazione),
    }
    if station_check.get("error"):
        station_validation["error"] = station_check["error"]

    return {
        "ok": True,
        "flow": "parse_only",
        "parsed_order": parsed.get("parsed_order", {}),
        "matched_fields": parsed.get("matched_fields", []),
        "unmatched_lines": parsed.get("unmatched_lines", []),
        "input_rows_count": parsed.get("input_rows_count", 0),
        "normalized": normalized_result.get("normalized", {}),
        "discrepancies": normalized_result.get("discrepancies", []),
        "has_meaningful_payload": normalized_result.get("has_meaningful_payload", False),
        "code_validation": code_validation,
        "station_validation": station_validation,
    }


def _agent_monitor(
    *,
    event_type: str,
    severity: str = "info",
    payload: dict | None = None,
) -> None:
    runtime = _get_agent_runtime()
    if runtime is None:
        return
    try:
        asyncio.run(
            runtime.analyze(
                source="api_smf",
                line_id="api_smf",
                event_type=event_type,
                severity=severity,
                payload=payload or {},
            )
        )
    except RuntimeError:
        pass
    except Exception:
        pass


def _get_agent_runtime():
    global agent_runtime
    if agent_runtime is not None:
        return agent_runtime
    try:
        from .agent_runtime.service import AgentRuntimeService
    except Exception:
        return None
    try:
        agent_runtime = AgentRuntimeService()
    except Exception:
        return None
    return agent_runtime


def _get_adapter() -> SMFAdapter:
    global adapter
    if adapter is None:
        adapter = SMFAdapter()
    return adapter


@router.get("/status")
def smf_status():
    _agent_monitor(
        event_type="smf_status_endpoint",
        payload={"endpoint": "/smf/status"},
    )
    return _get_adapter().info()


@router.get("/structure")
def smf_structure():
    _agent_monitor(
        event_type="smf_structure_endpoint",
        payload={"endpoint": "/smf/structure"},
    )
    return _get_adapter().structure()


@router.get("/preview")
def smf_preview(
    sheet: str | None = Query(default=None),
    rows: int = Query(default=5, ge=1, le=50),
):
    _agent_monitor(
        event_type="smf_preview_endpoint",
        payload={
            "endpoint": "/smf/preview",
            "sheet": sheet,
            "rows": rows,
        },
    )
    return _get_adapter().preview(sheet=sheet, rows=rows)


@router.get("/debug-bootstrap")
def smf_debug_bootstrap():
    adapter = _get_adapter()
    base_path = adapter.base_path
    master = adapter.master_path()

    # attempt a no-op bootstrap to record diagnostics if needed
    try:
        adapter._bootstrap_if_missing()  # type: ignore[attr-defined]
    except Exception:
        pass

    writable = False
    try:
        writable = adapter._writable_check(base_path)  # type: ignore[attr-defined]
    except Exception:
        writable = False

    return {
        "base_path": str(base_path),
        "master_path": str(master),
        "base_exists": base_path.exists(),
        "base_is_dir": base_path.is_dir(),
        "master_exists": master.exists(),
        "writable_check": writable,
        "bootstrap_attempted": bool(getattr(adapter, "_bootstrap_attempted", False)),
        "bootstrap_error": getattr(adapter, "_bootstrap_error", None),
    }


@router.post("/parse-extracted-order")
def smf_parse_extracted_order(payload: ParseExtractedOrderRequest):
    smf_adapter = _get_adapter()
    result = _build_parse_only_result(payload, smf_adapter=smf_adapter)

    _agent_monitor(
        event_type="smf_parse_extracted_order",
        severity="info",
        payload={
            "endpoint": "/smf/parse-extracted-order",
            "ok": True,
            "order_id": result.get("normalized", {}).get("order_id", ""),
            "discrepancies": len(result.get("discrepancies", [])),
            "matched_fields": len(result.get("matched_fields", [])),
            "code_validation": result.get("code_validation", {}).get("status", ""),
            "station_validation": result.get("station_validation", {}).get("status", ""),
        },
    )
    return result


@router.post("/parse-extracted-orders")
def smf_parse_extracted_orders(payload: list[ParseExtractedOrderRequest]):
    smf_adapter = _get_adapter()
    items: list[dict] = []
    seen_order_ids: set[str] = set()
    duplicates = 0

    for index, item_payload in enumerate(payload, start=1):
        item_result = _build_parse_only_result(item_payload, smf_adapter=smf_adapter)
        order_id = str(item_result.get("normalized", {}).get("order_id", "") or "").strip().upper()
        duplicate_in_request = bool(order_id and order_id in seen_order_ids)
        if order_id and not duplicate_in_request:
            seen_order_ids.add(order_id)
        if duplicate_in_request:
            duplicates += 1
        items.append(
            {
                "index": index,
                "duplicate_order_id_in_request": duplicate_in_request,
                **item_result,
            }
        )

    summary = {
        "total": len(items),
        "meaningful": sum(1 for item in items if item.get("has_meaningful_payload")),
        "warnings": sum(len(item.get("discrepancies", [])) for item in items),
        "errors": 0,
        "code_found": sum(1 for item in items if item.get("code_validation", {}).get("status") == "found"),
        "code_missing": sum(1 for item in items if item.get("code_validation", {}).get("status") == "missing"),
        "station_found": sum(1 for item in items if item.get("station_validation", {}).get("status") == "found"),
        "station_missing": sum(1 for item in items if item.get("station_validation", {}).get("status") == "missing"),
        "duplicates": duplicates,
    }

    result = {
        "ok": True,
        "flow": "parse_only_batch",
        "summary": summary,
        "items": items,
    }

    _agent_monitor(
        event_type="smf_parse_extracted_orders",
        severity="info",
        payload={
            "endpoint": "/smf/parse-extracted-orders",
            "ok": True,
            "total": summary["total"],
            "meaningful": summary["meaningful"],
            "warnings": summary["warnings"],
            "code_found": summary["code_found"],
            "code_missing": summary["code_missing"],
            "station_found": summary["station_found"],
            "station_missing": summary["station_missing"],
            "duplicates": summary["duplicates"],
        },
    )
    return result


@router.post("/ingest-extracted-order")
def smf_ingest_extracted_order(payload: ExtractedOrderIn):
    result = write_extracted_order_to_smf(payload, adapter=_get_adapter())
    _agent_monitor(
        event_type="smf_ingest_extracted_order",
        severity="info" if result.get("ok") else "medium",
        payload={
            "endpoint": "/smf/ingest-extracted-order",
            "ok": result.get("ok"),
            "order_id": result.get("normalized", {}).get("order_id", ""),
            "write_mode": result.get("smf_write", {}).get("mode", ""),
            "result_type": result.get("smf_write", {}).get("result_type", ""),
            "discrepancies": len(result.get("discrepancies", [])),
        },
    )
    return result


@router.post("/ingest-extracted-orders")
def smf_ingest_extracted_orders(payload: list[ExtractedOrderIn]):
    result = write_extracted_orders_to_smf(payload, adapter=_get_adapter())
    summary = result.get("summary", {})
    _agent_monitor(
        event_type="smf_ingest_extracted_orders",
        severity="info" if result.get("ok") else "medium",
        payload={
            "endpoint": "/smf/ingest-extracted-orders",
            "ok": result.get("ok"),
            "total": summary.get("total", 0),
            "written": summary.get("written", 0),
            "updated": summary.get("updated", 0),
            "appended": summary.get("appended", 0),
            "warnings": summary.get("warnings", 0),
            "errors": summary.get("errors", 0),
        },
    )
    return result
