from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.agent_mod.config import BASE_URL, ENDPOINTS
from app.agent_mod.contracts_registry import API_ENDPOINT_CONTRACTS
from app.agent_mod.models import CheckResult, GateResult, RunContext


def read_json_url(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        return resp.getcode(), json.loads(body)


def gate_g4(context: RunContext) -> GateResult:
    checks: list[CheckResult] = []

    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        try:
            status, payload = read_json_url(url)
            if status != 200:
                checks.append(
                    CheckResult(
                        name=f"probe:{endpoint}",
                        passed=False,
                        details=f"status {status}",
                    )
                )
                continue

            required_keys = API_ENDPOINT_CONTRACTS.get(endpoint, [])
            missing = [k for k in required_keys if k not in payload]
            checks.append(
                CheckResult(
                    name=f"probe:{endpoint}",
                    passed=(len(missing) == 0),
                    details="ok" if not missing else f"missing keys: {missing}",
                )
            )
        except urllib.error.HTTPError as exc:
            checks.append(
                CheckResult(
                    name=f"probe:{endpoint}",
                    passed=False,
                    details=f"http error {exc.code}",
                )
            )
        except Exception as exc:
            checks.append(
                CheckResult(
                    name=f"probe:{endpoint}",
                    passed=False,
                    details=str(exc),
                )
            )

    passed = all(c.passed for c in checks)
    return GateResult(gate="G4", passed=passed, checks=checks)
