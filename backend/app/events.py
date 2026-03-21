import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

EVENT_LOG = Path("data/events.log")


def append_event(event_type: str, payload: dict) -> dict:

    event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "payload": payload
    }

    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)

    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event
