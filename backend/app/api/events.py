from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.app.models.event import Event, EventClose, EventCreate, EventListResponse, EventUpdate
from backend.app.services.event_service import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
def list_events():
    items = event_service.list_events()
    open_count = len([e for e in items if e.status == "OPEN"])
    closed_count = len([e for e in items if e.status == "CLOSED"])

    return EventListResponse(
        total=len(items),
        open_count=open_count,
        closed_count=closed_count,
        items=items,
    )


@router.get("/active", response_model=list[Event])
def list_active_events():
    return event_service.list_active_events()


@router.post("/create", response_model=Event)
def create_event(payload: EventCreate):
    return event_service.create_event(payload)


@router.get("/{event_id}", response_model=Event)
def get_event(event_id: UUID):
    event = event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=Event)
def update_event(event_id: UUID, payload: EventUpdate):
    event = event_service.update_event(event_id, payload)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/close", response_model=Event)
def close_event(event_id: UUID, payload: EventClose):
    event = event_service.close_event(event_id, payload)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
