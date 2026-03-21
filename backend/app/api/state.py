from fastapi import APIRouter, HTTPException

from backend.app.services.event_service import event_service

router = APIRouter(prefix="/state", tags=["State"])


@router.get("")
def get_all_states():
    items = event_service.get_all_states()
    return {
        "total": len(items),
        "items": items,
    }


@router.get("/{line}/{station}")
def get_station_state(line: str, station: str):
    item = event_service.get_station_state(line=line, station=station)
    if not item:
        raise HTTPException(status_code=404, detail="State not found")
    return item
