from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.smf.smf_adapter import MASTER_NAME, _default_smf_dir
from app.smf.smf_reader import SMFReader


router = APIRouter()


class RealIngestOrderIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    order_id: str | None = Field(default=None)
    cliente: str | None = Field(default=None)
    codice: str | None = Field(default=None)
    qta: int | float | str | None = Field(default=None)
    due_date: str | None = Field(default=None)
    priority: str | None = Field(default=None)
    postazione: str | None = Field(default=None)
    route: list[str] | None = Field(default=None)
    note: str | None = Field(default=None)


class SMFRowPreview(BaseModel):
    id: str | None = None
    codice_articolo: str | None = None
    quantita: float | int | str | None = None
    cliente: str | None = None
    data_scadenza: str | None = None
    postazione_principale: str | None = None
    route: list[str] = Field(default_factory=list)
    stato: str = "DA_VALIDARE"
    origine: str = "REAL_INGEST_PREVIEW"


class RealIngestValidation(BaseModel):
    is_valid: bool
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_errors: list[str] = Field(default_factory=list)


class RealIngestCodeValidation(BaseModel):
    status: str
    found: bool
    sheet: str = "Codici"
    column: str = "Codice"
    matched_column: str | None = None
    code: str | None = None
    error: str | None = None


class RealIngestPreviewResponse(BaseModel):
    ok: bool
    validated: bool = True
    error: str | None = None
    smf_row_preview: SMFRowPreview | None = None
    validation: RealIngestValidation | None = None
    code_validation: RealIngestCodeValidation | None = None
    note: str = "Preview SMFRow — nessuna scrittura su SMF/database"


REQUIRED_FIELDS = ("order_id", "codice", "qta", "route")

STATION_ALIASES = {
    "ZAW1": "ZAW-1",
    "ZAW 1": "ZAW-1",
    "ZAW_1": "ZAW-1",
    "ZAW-1": "ZAW-1",
    "ZAW2": "ZAW-2",
    "ZAW 2": "ZAW-2",
    "ZAW_2": "ZAW-2",
    "ZAW-2": "ZAW-2",
    "PIDMILL": "PIDMILL",
    "HENN": "HENN",
    "FORNO": "FORNO",
    "WINTEC": "WINTEC",
    "ULTRASUONI": "ULTRASUONI",
    "CP": "CP",
}

KNOWN_ROUTE_STATIONS = set(STATION_ALIASES.values())
KNOWN_PRIORITIES = {"BASSA", "MEDIA", "ALTA", "CRITICA"}


def _normalize_quantity(value: int | float | str | None) -> tuple[float | None, str | None]:
    if value is None:
        return None, "qta_missing"

    if isinstance(value, str):
        raw = value.strip().replace(",", ".")
        if not raw:
            return None, "qta_missing"
    else:
        raw = value

    try:
        normalized = float(raw)
    except (TypeError, ValueError):
        return None, "qta_not_numeric"

    if normalized <= 0:
        return normalized, "qta_not_positive"

    return normalized, None


def _normalize_due_date(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None

    raw = str(value).strip()
    if not raw:
        return None, None

    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return raw, "due_date_not_iso"

    return parsed.isoformat(), None


def _normalize_priority(value: str | None) -> tuple[str, str | None]:
    if value is None:
        return "MEDIA", None

    raw = str(value).strip().upper()
    if not raw:
        return "MEDIA", None

    if raw not in KNOWN_PRIORITIES:
        return "MEDIA", "priority_unknown"

    return raw, None


def _get_smf_reader() -> SMFReader:
    """
    Read-only SMF access for preview endpoints.

    Do not instantiate SMFAdapter here:
    SMFAdapter bootstraps missing workbooks/directories and can write to disk.
    """
    return SMFReader(_default_smf_dir() / MASTER_NAME)


def _build_code_validation(codice: str | None, smf_reader: SMFReader) -> RealIngestCodeValidation:
    clean_code = str(codice or "").strip()

    if not clean_code:
        return RealIngestCodeValidation(
            status="DA_VERIFICARE",
            found=False,
            code=clean_code,
            error="empty_code",
        )

    code_check = smf_reader.code_exists(clean_code)

    status = "CERTO" if code_check.get("found") else "DA_VERIFICARE"

    return RealIngestCodeValidation(
        status=status,
        found=bool(code_check.get("found")),
        sheet=str(code_check.get("sheet", "Codici")),
        column=str(code_check.get("column", "Codice")),
        matched_column=code_check.get("matched_column"),
        code=str(code_check.get("code", clean_code)),
        error=code_check.get("error"),
    )


def _normalize_station(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip().upper()
    if not cleaned:
        return None

    return STATION_ALIASES.get(cleaned, cleaned)


def _field_is_missing(payload: RealIngestOrderIn, field_name: str) -> bool:
    if field_name not in payload.model_fields_set:
        return True

    value = getattr(payload, field_name)

    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


def _clean_route(route: list[str] | None) -> list[str]:
    if not route:
        return []

    cleaned: list[str] = []
    for item in route:
        normalized = _normalize_station(str(item))
        if normalized:
            cleaned.append(normalized)

    return cleaned


@router.post("/real/ingest-order", response_model=RealIngestPreviewResponse)
def ingest_real_order(
    payload: RealIngestOrderIn,
    db: Session = Depends(get_db),  # noqa: ARG001 - reserved for future controlled write phase
    smf_reader: SMFReader = Depends(_get_smf_reader),
) -> RealIngestPreviewResponse:
    """
    Ingest controllato articoli reali.

    Fase attuale:
    - valida il contratto minimo
    - costruisce preview SMFRow
    - non scrive su SMF
    - non scrive su database
    """
    missing = [field for field in REQUIRED_FIELDS if _field_is_missing(payload, field)]

    if missing:
        return RealIngestPreviewResponse(
            ok=False,
            error=f"missing_fields: {missing}",
            validation=RealIngestValidation(
                is_valid=False,
                missing_fields=missing,
                warnings=[],
                blocking_errors=["missing_required_fields"],
            ),
        )

    route = _clean_route(payload.route)

    normalized_qta, qta_error = _normalize_quantity(payload.qta)
    normalized_due_date, due_date_warning = _normalize_due_date(payload.due_date)
    normalized_priority, priority_warning = _normalize_priority(payload.priority)

    code_validation = _build_code_validation(payload.codice, smf_reader)

    smf_row_preview = SMFRowPreview(
        id=payload.order_id,
        codice_articolo=payload.codice,
        quantita=normalized_qta if normalized_qta is not None else payload.qta,
        cliente=payload.cliente,
        data_scadenza=normalized_due_date,
        postazione_principale=route[0] if route else None,
        route=route,
    )

    validation = RealIngestValidation(
        is_valid=True,
        missing_fields=[],
        warnings=[],
        blocking_errors=[],
    )

    if qta_error:
        validation.is_valid = False
        validation.blocking_errors.append(qta_error)

    if due_date_warning:
        validation.warnings.append(due_date_warning)

    if priority_warning:
        validation.warnings.append(priority_warning)

    if not route:
        validation.is_valid = False
        validation.blocking_errors.append("route_empty")

    unknown_stations = [station for station in route if station not in KNOWN_ROUTE_STATIONS]
    if unknown_stations:
        validation.is_valid = False
        validation.blocking_errors.append(f"unknown_route_stations: {unknown_stations}")

    declared_station = _normalize_station(payload.postazione)
    if declared_station and route and declared_station != route[0]:
        validation.warnings.append("postazione_mismatch_route_start")

    if code_validation.status == "DA_VERIFICARE":
        if code_validation.error:
            validation.warnings.append("codice_registry_non_accessibile")
        else:
            validation.warnings.append("codice_da_verificare")

    if route and route[-1] != "CP":
        validation.warnings.append("route_without_final_CP")

    return RealIngestPreviewResponse(
        ok=validation.is_valid,
        validated=True,
        smf_row_preview=smf_row_preview,
        validation=validation,
        code_validation=code_validation,
    )
