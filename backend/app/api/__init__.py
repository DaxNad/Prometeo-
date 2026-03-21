from fastapi import APIRouter

from .devos import router as devos_router

router = APIRouter()
router.include_router(devos_router)
