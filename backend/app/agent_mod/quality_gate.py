from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi.testclient import TestClient


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_pytest_quiet() -> Tuple[bool, Optional[str]]:
    try:
        # Find the repo root that contains pytest.ini to ensure consistent discovery
        here = Path(__file__).resolve()
        project_root = None
        for p in [here.parent, *here.parents]:
            if (p / "pytest.ini").exists():
                project_root = p
                break
        if project_root is None:
            project_root = here.parents[2]  # fallback to backend dir

        env = os.environ.copy()  # preserve current environment/venv
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        ok = proc.returncode == 0
        if ok:
            return True, None
        # Minimal diagnostic: last non-empty line from stderr or stdout
        err_lines = [l for l in (proc.stderr or "").strip().splitlines() if l.strip()]
        out_lines = [l for l in (proc.stdout or "").strip().splitlines() if l.strip()]
        tail = err_lines[-1] if err_lines else (out_lines[-1] if out_lines else "pytest failed")
        return False, tail
    except FileNotFoundError:
        return False, "pytest module not found"


def _build_client() -> TestClient:
    # Keep runtime untouched; only guide defaults for in-process checks
    os.environ.setdefault("PROMETEO_DB_BACKEND", "sqlite")
    os.environ.setdefault("DATABASE_URL", "")
    from app.main import app  # import after env defaults

    return TestClient(app)


def _auth_headers() -> dict[str, str]:
    try:
        from app.config import settings

        key = getattr(settings, "prometeo_api_key", "") or os.getenv("PROMETEO_API_KEY", "")
    except Exception:
        key = os.getenv("PROMETEO_API_KEY", "")

    return {"X-API-Key": key} if key else {}


def _check_health(client: TestClient) -> bool:
    r = client.get("/health")
    if r.status_code != 200:
        return False
    data = r.json()
    return bool(data.get("ok", data.get("status") == "ok"))


def _check_smf_status(client: TestClient) -> bool:
    r = client.get("/smf/status", headers=_auth_headers())
    if r.status_code != 200:
        return False
    data = r.json()
    # Endpoint may not expose explicit ok; validate stable shape
    if "ok" in data:
        return bool(data.get("ok"))
    return all(k in data for k in ("base_path", "path", "exists"))


def _check_parse_single(client: TestClient) -> bool:
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
    required = [
        "parsed_order",
        "normalized",
        "discrepancies",
        "code_validation",
        "station_validation",
    ]
    return bool(body.get("ok")) and all(k in body for k in required)


def _check_parse_batch(client: TestClient) -> bool:
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

    # summary-level checks
    summary_ok = "summary" in body and isinstance(body["summary"], dict)
    items = body.get("items", [])
    items_ok = isinstance(items, list) and len(items) >= 2

    # per-item checks for structure signals
    def _item_good(item: Dict[str, Any]) -> bool:
        return all(
            key in item for key in ("duplicate_order_id_in_request", "normalized", "has_meaningful_payload")
        )

    items_shape_ok = items_ok and all(_item_good(it) for it in items)
    return summary_ok and items_shape_ok


def run_quality_gate(*, run_pytest: bool = True) -> Dict[str, Any]:
    client = _build_client()

    pytest_ok: bool
    pytest_detail: Optional[str] = None
    if run_pytest:
        pytest_ok, pytest_detail = _run_pytest_quiet()
    else:
        pytest_ok = True

    checks = {
        "pytest": pytest_ok,
        "health": _check_health(client),
        "smf_status": _check_smf_status(client),
        "parse_single": _check_parse_single(client),
        "parse_batch": _check_parse_batch(client),
    }

    all_ok = all(checks.values())

    try:
        from app.config import settings
        version = settings.version
    except Exception:
        version = "unknown"

    result = {
        "quality_gate": "PASS" if all_ok else "FAIL",
        "checks": checks,
        "timestamp": _iso_now(),
        "version": version,
    }
    if not pytest_ok and pytest_detail:
        result["pytest_detail"] = pytest_detail
    return result


def _print_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False))


def main() -> None:
    res = run_quality_gate(run_pytest=True)
    _print_json(res)
    sys.exit(0 if res.get("quality_gate") == "PASS" else 1)


if __name__ == "__main__":
    main()
