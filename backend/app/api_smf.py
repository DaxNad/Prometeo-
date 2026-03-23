from fastapi import APIRouter

from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/smf", tags=["smf"])

adapter = SMFAdapter()


@router.get("/status")
def smf_status():
    return adapter.info()
