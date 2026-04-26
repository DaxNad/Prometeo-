from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ai-state", tags=["ai-state"])

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "ai_state"

PLANS_DIR = DATA_DIR / "plans"
EXECUTIONS_DIR = DATA_DIR / "executions"
CONTEXT_DIR = DATA_DIR / "context"

for d in (PLANS_DIR, EXECUTIONS_DIR, CONTEXT_DIR):
    d.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(p: Path, data: dict[str, Any]):
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def read_json(p: Path):
    if not p.exists():
        raise HTTPException(404, "not found")
    return json.loads(p.read_text())


def latest_file(dir: Path):
    files = sorted(dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None


class Plan(BaseModel):
    title: str
    target: str
    tasks: list[dict] = Field(default_factory=list)


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/plan")
def create_plan(p: Plan):
    pid = f"plan_{uuid4().hex[:8]}"
    doc = {
        "id": pid,
        "created_at": now(),
        **p.model_dump(),
    }
    write_json(PLANS_DIR / f"{pid}.json", doc)
    return {"ok": True, "id": pid}


@router.get("/plan/latest")
def latest_plan():
    f = latest_file(PLANS_DIR)
    if not f:
        raise HTTPException(404, "no plans")
    return read_json(f)
