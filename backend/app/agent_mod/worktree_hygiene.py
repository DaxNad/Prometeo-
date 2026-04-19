from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .worktree_models import DeployRisk, HygieneReport, WorktreeEntry


RUNTIME_PATTERNS = (
    "backend/app/data/",
)

JUNK_NAMES = {
    "1",
}

JUNK_SUFFIXES = (
    ".bak",
    ".tmp",
    ".temp",
    ".orig",
    ".rej",
    ".pyc",
)

JUNK_PARTS = {
    "__pycache__",
    ".prompts",
}

CORE_PREFIXES = (
    "backend/app/",
    "backend/sql/",
    "backend/tests/",
    "scripts/",
    ".github/workflows/",
    "railway.json",
    "AGENTS.md",
)

EXCLUDE_PREFIXES = (
    ".prompts/",
)

DEPLOY_REQUIRED_FILES = (
    "railway.json",
    "backend/requirements.txt",
)


def _run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def _run_bytes(cmd: list[str], cwd: Path) -> bytes:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstdout:\n{result.stdout.decode(errors='replace')}\nstderr:\n{result.stderr.decode(errors='replace')}"
        )
    return result.stdout


def _repo_root(start: Path) -> Path:
    return Path(_run(["git", "rev-parse", "--show-toplevel"], start))


def _current_branch(repo_root: Path) -> str:
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)


def _git_status_entries(repo_root: Path) -> list[tuple[str, str]]:
    raw = _run_bytes(["git", "status", "--porcelain=v1", "-z"], repo_root)
    if not raw:
        return []

    entries: list[tuple[str, str]] = []
    for chunk in raw.split(b"\x00"):
        if not chunk:
            continue

        line = chunk.decode("utf-8", errors="replace")
        if len(line) < 4:
            continue

        git_status = line[:2]
        path = line[3:]

        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()

        entries.append((git_status, path))

    return entries


def _is_runtime_artifact(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in RUNTIME_PATTERNS)


def _is_junk(path: str) -> tuple[bool, str]:
    p = Path(path)

    if p.name in JUNK_NAMES:
        return True, "single suspicious temp-like filename"

    if any(part in JUNK_PARTS for part in p.parts):
        return True, "cache/prompt/local auxiliary directory"

    if p.suffix.lower() in JUNK_SUFFIXES:
        return True, "backup/temp/generated suffix"

    if path.startswith(EXCLUDE_PREFIXES):
        return True, "local auxiliary path not meant for commit"

    return False, ""


def _is_core_change(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in CORE_PREFIXES) or path in {
        "railway.json",
        "AGENTS.md",
    }


def _classify_entry(git_status: str, path: str) -> WorktreeEntry:
    junk, junk_reason = _is_junk(path)
    if junk:
        return WorktreeEntry(
            path=path,
            git_status=git_status,
            category="junk_files",
            reason=junk_reason,
        )

    if _is_runtime_artifact(path):
        return WorktreeEntry(
            path=path,
            git_status=git_status,
            category="runtime_artifacts",
            reason="runtime snapshot/generated state",
        )

    if _is_core_change(path):
        return WorktreeEntry(
            path=path,
            git_status=git_status,
            category="core_changes",
            reason="matches backend/sql/tests/scripts tracked development area",
        )

    return WorktreeEntry(
        path=path,
        git_status=git_status,
        category="junk_files",
        reason="unclassified path outside protected core scope",
    )


def _deploy_risks(repo_root: Path) -> list[DeployRisk]:
    risks: list[DeployRisk] = []

    for required in DEPLOY_REQUIRED_FILES:
        if not (repo_root / required).exists():
            risks.append(
                DeployRisk(
                    code="MISSING_REQUIRED_FILE",
                    severity="BLOCK",
                    message=f"required deploy file missing: {required}",
                )
            )

    railway_path = repo_root / "railway.json"
    if railway_path.exists():
        try:
            data = json.loads(railway_path.read_text())
        except Exception as exc:
            risks.append(
                DeployRisk(
                    code="RAILWAY_JSON_INVALID",
                    severity="BLOCK",
                    message=f"railway.json is not valid JSON: {exc}",
                )
            )
        else:
            deploy = data.get("deploy", {})
            start_cmd = str(deploy.get("startCommand", "") or "")
            build_cmd = str(deploy.get("buildCommand", "") or "")

            if "backend/requirements.txt" in build_cmd and not (repo_root / "backend/requirements.txt").exists():
                risks.append(
                    DeployRisk(
                        code="BUILD_PATH_MISMATCH",
                        severity="BLOCK",
                        message="railway buildCommand references backend/requirements.txt but file is missing",
                    )
                )

            if "uvicorn" in start_cmd and "backend" not in start_cmd and "app.main:app" in start_cmd:
                risks.append(
                    DeployRisk(
                        code="START_PATH_REVIEW",
                        severity="WARN",
                        message="railway startCommand uses uvicorn app.main:app: verify working directory is backend/"
                    )
                )

    return risks


def build_worktree_hygiene_report(start_path: str | Path = ".") -> HygieneReport:
    start = Path(start_path).resolve()
    repo_root = _repo_root(start)
    branch = _current_branch(repo_root)
    entries = _git_status_entries(repo_root)

    report = HygieneReport(
        status="OK",
        repo_root=str(repo_root),
        branch=branch,
    )

    for git_status, path in entries:
        entry = _classify_entry(git_status=git_status, path=path)

        if entry.category == "core_changes":
            report.core_changes.append(entry)
            report.recommended_git_add.append(path)
        elif entry.category == "runtime_artifacts":
            report.runtime_artifacts.append(entry)
            report.recommended_exclude.append(path)
        else:
            report.junk_files.append(entry)
            report.recommended_exclude.append(path)

    report.deploy_risks.extend(_deploy_risks(repo_root))

    if report.junk_files:
        report.status = "BLOCK"
        report.notes.append("junk/local auxiliary files detected in working tree")

    if report.runtime_artifacts and report.status != "BLOCK":
        report.status = "WARN"
        report.notes.append("runtime artifacts detected; review before staging")

    if any(r.severity == "BLOCK" for r in report.deploy_risks):
        report.status = "BLOCK"
        report.notes.append("deploy blocking risks detected")

    if any(r.severity == "WARN" for r in report.deploy_risks) and report.status == "OK":
        report.status = "WARN"
        report.notes.append("deploy review warnings detected")

    report.recommended_git_add = sorted(set(report.recommended_git_add))
    report.recommended_exclude = sorted(set(report.recommended_exclude))

    if not entries:
        report.notes.append("working tree clean")

    return report


def main() -> int:
    report = build_worktree_hygiene_report(".")
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    return 0 if report.status in {"OK", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
