from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUNS_DIR = Path(__file__).resolve().parent / "runs"
RUNS_DIR.mkdir(exist_ok=True)

STATES = (
    "PLAN_READY",
    "TASK_GENERATED",
    "CODEX_APPLIED",
    "TESTS_PASSED",
    "CLAUDE_VALIDATED",
    "ACCEPTED",
    "FIX_REQUIRED",
    "ROLLBACK_REQUIRED",
    "SKIPPED",
)

CRITICAL_FILES = {
    "api_production.py",
    "sequence_planner.py",
    "drawing_registry_service.py",
    "bom_family_service.py",
    "executor/service.py",
    "ai_orchestrator/orchestrator.py",
}


def _run_path(task_id: str) -> Path:
    files = sorted(RUNS_DIR.glob(f"run_*_{task_id}.json"))
    if files:
        return files[-1]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return RUNS_DIR / f"run_{ts}_{task_id}.json"


def init_run(task_id: str, plan_id: str) -> dict[str, Any]:
    record = {
        "task_id": task_id,
        "plan_id": plan_id,
        "state": "TASK_GENERATED",
        "transitions": [
            {
                "from": None,
                "to": "TASK_GENERATED",
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "requires_claude": False,
        "notes": "",
    }
    _run_path(task_id).write_text(json.dumps(record, indent=2))
    return record


def advance(task_id: str, new_state: str, notes: str = "") -> dict[str, Any]:
    if new_state not in STATES:
        raise ValueError(f"Unknown state: {new_state}")

    path = _run_path(task_id)
    record = json.loads(path.read_text())
    record["transitions"].append(
        {
            "from": record["state"],
            "to": new_state,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    )
    record["state"] = new_state
    if notes:
        record["notes"] = notes
    path.write_text(json.dumps(record, indent=2))
    return record


def mark_requires_claude(task_id: str, files_changed: list[str]) -> bool:
    path = _run_path(task_id)
    record = json.loads(path.read_text())
    requires = any(any(cf in f for cf in CRITICAL_FILES) for f in files_changed)
    record["requires_claude"] = requires
    path.write_text(json.dumps(record, indent=2))
    return requires


def load_run(task_id: str) -> dict[str, Any] | None:
    path = _run_path(task_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())
