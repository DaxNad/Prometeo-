from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi.testclient import TestClient


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_client() -> TestClient:
    # Ensure local, deterministic runtime for schema checks
    os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
    os.environ.setdefault("DATABASE_URL", "")
    from app.main import app  # noqa: WPS433 (import after env set)

    return TestClient(app)


def _auth_headers() -> dict[str, str]:
    try:
        from app.config import settings

        key = getattr(settings, "prometeo_api_key", "") or os.getenv("PROMETEO_API_KEY", "")
    except Exception:
        key = os.getenv("PROMETEO_API_KEY", "")

    return {"X-API-Key": key} if key else {}


def _check_health_schema(client: TestClient) -> bool:
    r = client.get("/health")
    if r.status_code != 200:
        return False
    data = r.json()
    ok = bool(data.get("ok", data.get("status") == "ok"))
    version_ok = isinstance(data.get("version"), str) and len(data.get("version")) > 0
    return ok and version_ok


def _check_smf_status_schema(client: TestClient) -> bool:
    r = client.get("/smf/status", headers=_auth_headers())
    if r.status_code != 200:
        return False
    data = r.json()
    required = ("base_path", "path", "exists")
    return all(k in data for k in required)


def _check_parse_single_schema(client: TestClient) -> bool:
    payload = {
        "order_id": "QG-001",
        "code": "12063",
        "quantity": 1,
        "station": "ZAW-1",
        "customer_due_date": "2026-04-15",
    }
    r = client.post("/smf/parse-extracted-order", json=payload, headers=_auth_headers())
    if r.status_code != 200:
        return False
    body = r.json()
    req = [
        "parsed_order",
        "normalized",
        "discrepancies",
        "code_validation",
        "station_validation",
    ]
    return bool(body.get("ok")) and all(k in body for k in req)


def _check_parse_batch_schema(client: TestClient) -> bool:
    payload = [
        {
            "order_id": "QG-BATCH-001",
            "code": "12063",
            "quantity": 1,
            "station": "ZAW-1",
            "customer_due_date": "2026-04-15",
        },
        {
            "order_id": "QG-BATCH-001",
            "code": "12063",
            "quantity": 1,
            "station": "ZAW-1",
            "customer_due_date": "2026-04-15",
        },
    ]
    r = client.post("/smf/parse-extracted-orders", json=payload, headers=_auth_headers())
    if r.status_code != 200:
        return False
    body = r.json()
    if not body.get("ok"):
        return False
    summary_ok = isinstance(body.get("summary"), dict)
    items = body.get("items", [])
    if not isinstance(items, list):
        return False
    def _item_ok(item: Dict[str, Any]) -> bool:
        return all(k in item for k in ("duplicate_order_id_in_request", "normalized", "has_meaningful_payload"))
    items_ok = all(_item_ok(it) for it in items)
    # Soft cardinality: accept 0..N items; verify shape only for present items
    return summary_ok and items_ok


def run_schema_guard() -> Dict[str, Any]:
    client = _build_client()
    checks = {
        "health_schema": _check_health_schema(client),
        "smf_status_schema": _check_smf_status_schema(client),
        "parse_single_schema": _check_parse_single_schema(client),
        "parse_batch_schema": _check_parse_batch_schema(client),
    }
    all_ok = all(checks.values())
    try:
        from app.config import settings
        version = settings.version
    except Exception:
        version = "unknown"
    result = {
        "schema_guard": "PASS" if all_ok else "FAIL",
        "checks": checks,
        "timestamp": _iso_now(),
        "version": version,
    }
    return result


def main() -> None:
    res = run_schema_guard()
    print(json.dumps(res, ensure_ascii=False))
    sys.exit(0 if res.get("schema_guard") == "PASS" else 1)


if __name__ == "__main__":
    main()
