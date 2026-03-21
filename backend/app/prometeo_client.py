import os
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timezone

PROMETEO_API = os.getenv(
    "PROMETEO_API",
    "https://prometeo-railway-bootstrap-production.up.railway.app",
)

TIMEOUT_S = float(os.getenv("PROMETEO_TIMEOUT", "5"))


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def push_event(
    title: str,
    status: str = "ACTIVE",
    area: str = "PROD",
    note: Optional[str] = None,
    code: Optional[str] = None,
    station: Optional[str] = None,
    shift: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "title": title,
        "status": status,
        "area": area,
        "note": note,
        "code": code,
        "station": station,
        "shift": shift,
        "ts_local": _utc_now_z(),
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{PROMETEO_API}/api/events/append",
        json=payload,
        timeout=TIMEOUT_S,
    )
    r.raise_for_status()
    return r.json()
