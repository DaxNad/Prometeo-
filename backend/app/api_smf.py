import asyncio
import json
import re

import pandas as pd

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



def _read_smf_sheet(sheet_name: str) -> pd.DataFrame:
    master_path = _get_adapter().master_path()
    return pd.read_excel(master_path, sheet_name=sheet_name)


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


_COMPONENT_CODE_RE = re.compile(r"\b(?:\d{6}|[A-Z]{2,5}\d{3,4})\b")


def _safe_json_loads(value: object) -> object | None:
    if isinstance(value, (dict, list)):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _collect_component_codes(*values: object) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            for item in node.values():
                _walk(item)
            return
        if isinstance(node, list):
            for item in node:
                _walk(item)
            return
        text = str(node or "").upper()
        for match in _COMPONENT_CODE_RE.findall(text):
            if match not in seen:
                seen.add(match)
                matches.append(match)

    for value in values:
        parsed = _safe_json_loads(value)
        _walk(parsed if parsed is not None else value)

    return matches


def _append_unique(target: list[str], values: list[str], *, skip: set[str] | None = None) -> None:
    existing = set(target)
    ignored = skip or set()
    for value in values:
        if value in existing or value in ignored:
            continue
        target.append(value)
        existing.add(value)


def _infer_tipo_famiglia(articoli: list[str], family_specs: pd.DataFrame) -> str:
    unique_articoli = {str(value).strip() for value in articoli if str(value).strip()}
    if len(unique_articoli) >= 3:
        return "famiglia_complessivo"
    family_markers = " ".join(
        family_specs.get("famiglia_processo", pd.Series(dtype=str)).astype(str).str.upper().tolist()
    )
    if "BASE" in family_markers and len(unique_articoli) == 1:
        return "lineare"
    return "famiglia"


def _infer_tassativo(
    articoli: list[str],
    family_specs: pd.DataFrame,
    var_family: pd.DataFrame,
) -> bool:
    payload = " ".join(
        family_specs.get("raw_json", pd.Series(dtype=str)).astype(str).tolist()
        + var_family.astype(str).agg(" ".join, axis=1).tolist()
        + articoli
    ).upper()
    has_partial = any(token in payload for token in ("PARZIALE", "PARTIAL"))
    has_group = any(token in payload for token in ("COMPLESSIVO", "COMPLESSIVI", "GRUPPO", "ASSIEME"))
    return has_partial and has_group


def _infer_rotazione(
    *,
    articoli: list[str],
    componenti_unici: list[str],
    fasi_uniche: list[str],
    count_markings: int,
) -> str:
    fase_tokens = " ".join(fasi_uniche).upper()
    fast_lane = not any(token in fase_tokens for token in ("PIDMILL", "HENN", "ZAW", "COLLAUDO", "CP"))
    single_linear = len(articoli) == 1 and len(componenti_unici) <= 2 and len(fasi_uniche) <= 3 and count_markings <= 1
    return "alta" if single_linear and fast_lane else "da_verificare"


def _build_peso_turno(
    *,
    postazioni_stimate: list[str],
    count_markings: int,
    count_componenti: int,
    count_articoli: int,
) -> dict:
    per_postazione: dict[str, int] = {}
    driver: list[str] = []
    totale = 1

    if "PIDMILL" in postazioni_stimate:
        per_postazione["PIDMILL"] = per_postazione.get("PIDMILL", 0) + 2
        driver.append("peso_pidmill")
        totale += 2
    if "HENN" in postazioni_stimate:
        per_postazione["HENN"] = per_postazione.get("HENN", 0) + 2
        driver.append("peso_henn")
        totale += 2
    if count_markings >= 2:
        driver.append("multi_marcatura")
        totale += 2
    if count_componenti > 4:
        driver.append("multi_component")
        totale += 1
    if count_articoli >= 3:
        driver.append("famiglia_ampia")
        totale += 1

    livello = "alto" if totale >= 5 else "medio" if totale >= 3 else "basso"
    return {
        "totale": totale,
        "livello": livello,
        "driver": driver,
        "per_postazione": per_postazione,
    }


@router.get("/bom/specs")
def smf_bom_specs(
    articolo: str | None = Query(default=None),
    disegno: str | None = Query(default=None),
):
    df = _read_smf_sheet("BOM_Specs").fillna("")
    if articolo:
        df = df[df["articolo"].astype(str).str.strip() == articolo.strip()]
    if disegno:
        df = df[df["disegno"].astype(str).str.replace(" ", "", regex=False) == disegno.strip().replace(" ", "")]
    return {
        "ok": True,
        "sheet": "BOM_Specs",
        "count": len(df),
        "items": df.to_dict(orient="records"),
    }




@router.get("/bom/family-summary/by-drawing")
def smf_family_summary_by_drawing(
    disegno: str = Query(...),
):
    specs = _read_smf_sheet("BOM_Specs").fillna("")
    components = _read_smf_sheet("BOM_Components").fillna("")
    operations = _read_smf_sheet("BOM_Operations").fillna("")
    markings = _read_smf_sheet("BOM_Markings").fillna("")
    variants = _read_smf_sheet("BOM_Variants").fillna("")

    target = str(disegno).strip().replace(" ", "")

    normalized_specs = specs["disegno"].astype(str).str.replace(" ", "", regex=False)

    family_specs = specs[normalized_specs == target].copy()

    articoli = family_specs["articolo"].astype(str).tolist()

    comp_family = components[components["articolo"].astype(str).isin(articoli)]
    op_family = operations[operations["articolo"].astype(str).isin(articoli)]
    mark_family = markings[markings["articolo"].astype(str).isin(articoli)]
    var_family = variants[variants["articolo"].astype(str).isin(articoli)]

    componenti_unici: list[str] = []
    articoli_set = {str(value).strip().upper() for value in articoli if str(value).strip()}

    direct_componenti = (
        comp_family["codice_componente"]
        .astype(str)
        .replace("", None)
        .dropna()
        .str.upper()
        .unique()
        .tolist()
    )
    _append_unique(componenti_unici, direct_componenti, skip=articoli_set)

    if "raw_json" in family_specs.columns:
        for raw in family_specs["raw_json"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(raw), skip=articoli_set)

    if "extra" in comp_family.columns:
        for extra in comp_family["extra"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(extra), skip=articoli_set)

    if "extra" in op_family.columns:
        for extra in op_family["extra"].tolist():
            _append_unique(componenti_unici, _collect_component_codes(extra), skip=articoli_set)

    fasi_uniche = (
        op_family["fase"]
        .astype(str)
        .replace("", None)
        .dropna()
        .unique()
        .tolist()
    )

    postazioni_stimate = []

    for fase in fasi_uniche:

        f = fase.upper()

        if "GUAINA" in f:
            postazioni_stimate.append("GUAINE")

        if "PIDMILL" in f:
            postazioni_stimate.append("PIDMILL")

        if "ZAW" in f:
            postazioni_stimate.append("ZAW")

        if "HENN" in f:
            postazioni_stimate.append("HENN")

        if "CP" in f or "COLLAUDO" in f:
            postazioni_stimate.append("CP")

    postazioni_stimate = sorted(set(postazioni_stimate))
    count_markings = len(mark_family.index)

    criticita = []

    if "GUAINE" in postazioni_stimate:
        criticita.append("carico_guaina")

    if len(componenti_unici) > 4:
        criticita.append("multi_component")

    if "PIDMILL" in postazioni_stimate:
        criticita.append("tempo_pidmill")

    if "ZAW" in postazioni_stimate:
        criticita.append("tempo_zaw")

    tipo_famiglia = _infer_tipo_famiglia(articoli, family_specs)
    tassativo = _infer_tassativo(articoli, family_specs, var_family)
    rotazione = _infer_rotazione(
        articoli=articoli,
        componenti_unici=componenti_unici,
        fasi_uniche=fasi_uniche,
        count_markings=count_markings,
    )
    peso_turno = _build_peso_turno(
        postazioni_stimate=postazioni_stimate,
        count_markings=count_markings,
        count_componenti=len(componenti_unici),
        count_articoli=len(articoli),
    )

    return {

        "ok": True,

        "drawing": disegno,

        "normalized_drawing": target,

        "articoli_famiglia": articoli,

        "count_articoli": len(articoli),

        "componenti_coinvolti": componenti_unici,

        "count_componenti": len(componenti_unici),

        "fasi_coinvolte": fasi_uniche,

        "postazioni_stimate": postazioni_stimate,

        "criticita_tl": criticita,

        "rotazione": rotazione,

        "tassativo": tassativo,

        "peso_turno": peso_turno,

        "tipo_famiglia": tipo_famiglia,

        "raw": {

            "specs": family_specs.to_dict(orient="records"),

            "components": comp_family.to_dict(orient="records"),

            "operations": op_family.to_dict(orient="records"),

            "markings": mark_family.to_dict(orient="records"),

            "variants": var_family.to_dict(orient="records"),

        }

    }


@router.get("/bom/specs/by-drawing")
def smf_bom_specs_by_drawing(
    disegno: str = Query(...),
):
    df = _read_smf_sheet("BOM_Specs").fillna("")

    target = str(disegno or "").strip().replace(" ", "")

    if "disegno" not in df.columns:
        return {
            "ok": False,
            "sheet": "BOM_Specs",
            "disegno": disegno,
            "count": 0,
            "items": [],
            "error": "column disegno not found"
        }

    normalized = df["disegno"].astype(str).str.strip().str.replace(" ", "", regex=False)

    df = df[normalized == target].copy()

    if "articolo" in df.columns:
        try:
            df = df.sort_values(by=["articolo"])
        except Exception:
            pass

    return {
        "ok": True,
        "sheet": "BOM_Specs",
        "disegno": disegno,
        "normalized_disegno": target,
        "count": len(df),
        "items": df.to_dict(orient="records"),
    }


@router.get("/bom/components/by-article")
def smf_bom_components_by_article(
    articolo: str = Query(...),
):
    df = _read_smf_sheet("BOM_Components").fillna("")
    df = df[df["articolo"].astype(str).str.strip() == articolo.strip()]
    return {
        "ok": True,
        "sheet": "BOM_Components",
        "articolo": articolo,
        "count": len(df),
        "items": df.to_dict(orient="records"),
    }


@router.get("/bom/components/by-component")
def smf_bom_components_by_component(
    codice_componente: str = Query(...),
):
    df = _read_smf_sheet("BOM_Components").fillna("")
    df = df[df["codice_componente"].astype(str).str.strip() == codice_componente.strip()]
    return {
        "ok": True,
        "sheet": "BOM_Components",
        "codice_componente": codice_componente,
        "count": len(df),
        "items": df.to_dict(orient="records"),
    }


@router.get("/bom/operations/by-article")
def smf_bom_operations_by_article(
    articolo: str = Query(...),
):
    df = _read_smf_sheet("BOM_Operations").fillna("")
    df = df[df["articolo"].astype(str).str.strip() == articolo.strip()]
    if "seq_no" in df.columns:
        try:
            df = df.sort_values(by=["seq_no"])
        except Exception:
            pass
    return {
        "ok": True,
        "sheet": "BOM_Operations",
        "articolo": articolo,
        "count": len(df),
        "items": df.to_dict(orient="records"),
    }


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

    # keep diagnostics concise and production-safe
    err = getattr(adapter, "_bootstrap_error", None)
    err_summary = None
    if isinstance(err, str) and err.strip():
        try:
            err_summary = err.strip().splitlines()[-1]
        except Exception:
            err_summary = "bootstrap_error"

    schema = adapter.validate_structure()

    return {
        "base_path": str(base_path),
        "master_path": str(master),
        "base_exists": base_path.exists(),
        "base_is_dir": base_path.is_dir(),
        "master_exists": master.exists(),
        "writable_check": writable,
        "bootstrap_attempted": bool(getattr(adapter, "_bootstrap_attempted", False)),
        "bootstrap_error": err_summary,
        "schema_ok": bool(schema.get("ok")),
        "missing_counts": {
            "sheets": len(schema.get("sheets_missing", [])),
            "columns": sum(len(v) for v in schema.get("columns_missing", {}).values()),
        },
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
