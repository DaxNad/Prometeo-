from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"

CRITICAL_PREFIXES = [
    "backend/app/services",
    "backend/app/api",
    "backend/app/planners",
    "backend/app/rule_engine",
    "backend/sql",
    "backend/app/data",
]

ENDPOINTS = [
    "/health",
    "/production/sequence",
    "/production/turn-plan",
    "/production/machine-load",
]

HEALTH_URL = "http://127.0.0.1:8000/health"
BASE_URL = "http://127.0.0.1:8000"
SNAPSHOT_DIR = ROOT_DIR / "board" / "agent_mod_snapshots"

START_CMD = ["bash", "scripts/dev_start.sh"]
STOP_CMD = ["bash", "scripts/dev_stop.sh"]
STATUS_CMD = ["bash", "scripts/dev_status.sh"]
