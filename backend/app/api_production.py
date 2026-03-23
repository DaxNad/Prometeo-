from fastapi import APIRouter

from .smf.smf_adapter import SMFAdapter

router = APIRouter(prefix="/production", tags=["production"])

adapter = SMFAdapter()


@router.get("/orders")
def production_orders():
    return adapter.preview(sheet="Pianificazione", rows=200)


@router.get("/stations")
def production_stations():
    return adapter.preview(sheet="Postazioni", rows=200)


@router.get("/teamleaders")
def production_teamleaders():
    return adapter.preview(sheet="TurniTL", rows=200)


@router.post("/order")
def create_order(order: dict):
    return adapter.append_order(order)


@router.patch("/order/{order_id}")
def update_order(order_id: str, updates: dict):
    return adapter.update_order(order_id, updates)
