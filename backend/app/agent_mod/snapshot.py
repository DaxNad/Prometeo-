from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from app.agent_mod.config import ROOT_DIR, SNAPSHOT_DIR
from app.agent_mod.models import CheckResult, GateResult, RunContext


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def current_branch() -> str:
    code, out, err = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT_DIR)
    return out if code == 0 else "unknown"


def current_commit() -> str:
    code, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR)
    return out if code == 0 else "unknown"


def gate_g5(context: RunContext, prior_gates: list[GateResult]) -> GateResult:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    files = context.files or []
    hashes = {}
    for rel in files:
        path = ROOT_DIR / rel
        if path.exists() and path.is_file():
            hashes[rel] = sha256_file(path)

    snapshot = {
        "timestamp": datetime.now(UTC).isoformat(),
        "branch": current_branch(),
        "commit": current_commit(),
        "files": files,
        "hashes": hashes,
        "gates": [
            {
                "gate": g.gate,
                "passed": g.passed,
                "checks": [
                    {
                        "name": c.name,
                        "passed": c.passed,
                        "details": c.details,
                    }
                    for c in g.checks
                ],
            }
            for g in prior_gates
        ],
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = SNAPSHOT_DIR / f"agent_mod_snapshot_{ts}.json"
    out_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return GateResult(
        gate="G5",
        passed=True,
        checks=[
            CheckResult(
                name="snapshot_written",
                passed=True,
                details=str(out_path),
            )
        ],
    )
