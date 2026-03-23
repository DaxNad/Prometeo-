from fastapi import APIRouter, Query

from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/smf", tags=["smf"])

adapter = SMFAdapter()


@router.get("/status")
def smf_status():
    return adapter.info()


@router.get("/structure")
def smf_structure():
    return adapter.structure()


@router.get("/preview")
def smf_preview(
    sheet: str | None = Query(default=None),
    rows: int = Query(default=5, ge=1, le=50),
):
    return adapter.preview(sheet=sheet, rows=rows)
