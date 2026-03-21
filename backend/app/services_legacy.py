from .repository import insert_event, list_events


def add_event_service(event):
    return insert_event(
        code=event.code,
        station=event.station,
        event_type=event.event_type,
        operator=event.operator,
    )


def get_events_service():
    return list_events()
