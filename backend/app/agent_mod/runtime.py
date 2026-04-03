from __future__ import annotations

import subprocess
import time
from pathlib import Path

from app.agent_mod.config import HEALTH_URL, ROOT_DIR, START_CMD, STATUS_CMD, STOP_CMD
from app.agent_mod.models import CheckResult, GateResult, RunContext
from app.agent_mod.probes import read_json_url


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def wait_health(timeout_sec: int = 30) -> CheckResult:
    deadline = time.time() + timeout_sec
    last_error = ""
    while time.time() < deadline:
        try:
            status, payload = read_json_url(HEALTH_URL)
            if status == 200 and isinstance(payload, dict):
                return CheckResult(
                    name="health_ready",
                    passed=True,
                    details="runtime pronto",
                    data=payload,
                )
        except Exception as exc:
            last_error = str(exc)
        time.sleep(1)
    return CheckResult(
        name="health_ready",
        passed=False,
        details=f"timeout health: {last_error}",
    )


def gate_g3(context: RunContext) -> GateResult:
    if context.skip_runtime:
        return GateResult(
            gate="G3",
            passed=True,
            checks=[
                CheckResult(
                    name="runtime_skipped",
                    passed=True,
                    details="skip runtime attivo",
                )
            ],
        )

    checks: list[CheckResult] = []

    code, out, err = run_cmd(STOP_CMD, cwd=ROOT_DIR)
    checks.append(
        CheckResult(
            name="runtime_stop",
            passed=(code == 0),
            details=out or err or "stop eseguito",
        )
    )

    code, out, err = run_cmd(START_CMD, cwd=ROOT_DIR)
    checks.append(
        CheckResult(
            name="runtime_start",
            passed=(code == 0),
            details=out or err or "start eseguito",
        )
    )

    checks.append(wait_health())

    code, out, err = run_cmd(STATUS_CMD, cwd=ROOT_DIR)
    checks.append(
        CheckResult(
            name="runtime_status",
            passed=(code == 0),
            details=out or err or "status eseguito",
        )
    )

    passed = all(c.passed for c in checks)
    return GateResult(gate="G3", passed=passed, checks=checks)
