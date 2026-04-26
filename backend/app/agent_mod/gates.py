from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

from app.agent_mod.config import CRITICAL_PREFIXES, ROOT_DIR
from app.agent_mod.contracts_registry import (
    API_MODULE_CONTRACTS,
    RUNTIME_DATA_CONTRACTS,
    SERVICE_SQL_CONTRACTS,
)
from app.agent_mod.inspector import attach_categories
from app.agent_mod.models import CheckResult, GateResult, RunContext


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def discover_git_changed_files() -> list[str]:
    code, out, err = run_cmd(["git", "status", "--porcelain"], cwd=ROOT_DIR)
    if code != 0:
        return []
    files: list[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if parts:
            files.append(parts[-1])
    return files


def gate_g1(context: RunContext) -> GateResult:
    files = context.files or discover_git_changed_files()
    critical = [
        f for f in files
        if any(f.startswith(prefix) for prefix in CRITICAL_PREFIXES)
    ]

    context.files = files
    attach_categories(context)

    checks = [
        CheckResult(
            name="changed_files_detected",
            passed=True,
            details=f"{len(files)} file rilevati",
            data={"files": files},
        ),
        CheckResult(
            name="critical_scope",
            passed=True,
            details=f"{len(critical)} file critici",
            data={"critical_files": critical},
        ),
        CheckResult(
            name="classified_scope",
            passed=True,
            details="categorie assegnate",
            data={"categories": context.categories},
        ),
    ]
    return GateResult(gate="G1", passed=True, checks=checks)


def _check_sql_contracts(checks: list[CheckResult]) -> None:
    sql_dir = ROOT_DIR / "backend" / "sql"
    sql_files = list(sql_dir.glob("*.sql")) if sql_dir.exists() else []
    sql_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in sql_files
    )

    for service_name, contract in SERVICE_SQL_CONTRACTS.items():
        for view_name in contract["views"]:
            exists_in_repo = view_name in sql_text
            checks.append(
                CheckResult(
                    name=f"view_declared:{service_name}:{view_name}",
                    passed=exists_in_repo,
                    details=f"view {'trovata' if exists_in_repo else 'non trovata'} negli sql",
                )
            )


def _check_api_module_contracts(checks: list[CheckResult]) -> None:
    for module_name in API_MODULE_CONTRACTS.get("critical_modules", []):
        try:
            importlib.import_module(module_name)
            checks.append(
                CheckResult(
                    name=f"api_module_import:{module_name}",
                    passed=True,
                    details="import ok",
                )
            )
        except Exception as exc:
            checks.append(
                CheckResult(
                    name=f"api_module_import:{module_name}",
                    passed=False,
                    details=str(exc),
                )
            )


def _check_runtime_data_contracts(checks: list[CheckResult]) -> None:
    for rel_path, expected_type in RUNTIME_DATA_CONTRACTS.items():
        path = ROOT_DIR / rel_path
        ok = path.exists()
        if ok:
            try:
                if expected_type == "json":
                    json.loads(path.read_text(encoding="utf-8"))
                checks.append(
                    CheckResult(
                        name=f"runtime_contract:{rel_path}",
                        passed=True,
                        details=f"{expected_type} valido",
                    )
                )
            except Exception as exc:
                checks.append(
                    CheckResult(
                        name=f"runtime_contract:{rel_path}",
                        passed=False,
                        details=str(exc),
                    )
                )
        else:
            checks.append(
                CheckResult(
                    name=f"runtime_contract:{rel_path}",
                    passed=False,
                    details="file assente",
                )
            )


def gate_g2(context: RunContext) -> GateResult:
    checks: list[CheckResult] = []
    categories = context.categories or {}

    sql_changed = bool(categories.get("sql"))
    runtime_data_changed = bool(categories.get("runtime_data"))
    service_changed = bool(categories.get("service"))
    planner_changed = bool(categories.get("planner"))
    api_changed = bool(categories.get("api"))

    should_check_sql_contracts = sql_changed or service_changed or planner_changed or api_changed
    should_check_api_imports = service_changed or planner_changed or api_changed
    should_check_runtime_data = runtime_data_changed

    if not should_check_sql_contracts and not should_check_api_imports and not should_check_runtime_data:
        checks.append(
            CheckResult(
                name="g2_scope_skip",
                passed=True,
                details="nessun file sql/runtime-data/service/api/planner coinvolto",
                data={"categories": categories},
            )
        )
        return GateResult(gate="G2", passed=True, checks=checks)

    if should_check_sql_contracts:
        _check_sql_contracts(checks)
    else:
        checks.append(
            CheckResult(
                name="sql_contracts_skipped",
                passed=True,
                details="nessuna modifica rilevante per contract sql",
            )
        )

    if should_check_api_imports:
        _check_api_module_contracts(checks)
    else:
        checks.append(
            CheckResult(
                name="api_module_contracts_skipped",
                passed=True,
                details="nessuna modifica rilevante per import API",
            )
        )

    if should_check_runtime_data:
        _check_runtime_data_contracts(checks)
    else:
        checks.append(
            CheckResult(
                name="runtime_data_skipped",
                passed=True,
                details="nessuna modifica ai file runtime-data",
            )
        )

    passed = all(c.passed for c in checks)
    return GateResult(gate="G2", passed=passed, checks=checks)


def gate_g6(prior_gates: list[GateResult]) -> GateResult:
    allowed = all(g.passed for g in prior_gates)
    return GateResult(
        gate="G6",
        passed=allowed,
        checks=[
            CheckResult(
                name="freeze_commit",
                passed=allowed,
                details="commit consentito" if allowed else "commit bloccato",
            )
        ],
    )


def gate_g0_operational_backbone(context: RunContext) -> GateResult:
    master_path = ROOT_DIR / "docs" / "PROMETEO_MASTER.md"

    required_markers = [
        "## PROMETEO — Colonna Vertebrale Operativa",
        "docs/PROMETEO_MASTER.md",
        "Agent Mod",
        "Guard rails pre-modifica",
        "Test minimi obbligatori",
        "Order → Route → Station → ProductionEvent",
        "Divieto di dispersione memoria",
        "Regola anti-branch separati",
        "Gate obbligatorio prima di ogni modifica",
    ]

    checks: list[CheckResult] = []

    if not master_path.exists():
        checks.append(
            CheckResult(
                name="operational_backbone_master_exists",
                passed=False,
                details="docs/PROMETEO_MASTER.md assente",
            )
        )
        return GateResult(gate="G0", passed=False, checks=checks)

    text = master_path.read_text(encoding="utf-8", errors="ignore")
    missing = [m for m in required_markers if m not in text]

    checks.append(
        CheckResult(
            name="operational_backbone_declared",
            passed=not missing,
            details="colonna vertebrale presente" if not missing else "marker mancanti: " + ", ".join(missing),
            data={"missing_markers": missing},
        )
    )

    return GateResult(gate="G0", passed=all(c.passed for c in checks), checks=checks)
