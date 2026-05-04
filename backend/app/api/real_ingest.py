from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.smf.smf_adapter import SMFAdapter


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
    quantita: int | float | str | None = None
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


def _get_smf_adapter() -> SMFAdapter:
    return SMFAdapter()


def _build_code_validation(codice: str | None, smf_adapter: SMFAdapter) -> RealIngestCodeValidation:
    clean_code = str(codice or "").strip()

    if not clean_code:
        return RealIngestCodeValidation(
            status="DA_VERIFICARE",
            found=False,
            code=clean_code,
            error="empty_code",
        )

    code_check = smf_adapter.reader().code_exists(clean_code)

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
    smf_adapter: SMFAdapter = Depends(_get_smf_adapter),
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

    code_validation = _build_code_validation(payload.codice, smf_adapter)

    smf_row_preview = SMFRowPreview(
        id=payload.order_id,
        codice_articolo=payload.codice,
        quantita=payload.qta,
        cliente=payload.cliente,
        data_scadenza=payload.due_date,
        postazione_principale=route[0] if route else None,
        route=route,
    )

    validation = RealIngestValidation(
        is_valid=True,
        missing_fields=[],
        warnings=[],
        blocking_errors=[],
    )

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
