from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import get_db


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


class RealIngestPreviewResponse(BaseModel):
    ok: bool
    validated: bool = True
    error: str | None = None
    smf_row_preview: SMFRowPreview | None = None
    validation: RealIngestValidation | None = None
    note: str = "Preview SMFRow — nessuna scrittura su SMF/database"


REQUIRED_FIELDS = ("order_id", "codice", "qta", "route")


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

    return [str(item).strip() for item in route if str(item).strip()]


@router.post("/real/ingest-order", response_model=RealIngestPreviewResponse)
def ingest_real_order(
    payload: RealIngestOrderIn,
    db: Session = Depends(get_db),  # noqa: ARG001 - reserved for future controlled write phase
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

    if route and route[-1] != "CP":
        validation.warnings.append("route_without_final_CP")

    return RealIngestPreviewResponse(
        ok=validation.is_valid,
        validated=True,
        smf_row_preview=smf_row_preview,
        validation=validation,
    )
