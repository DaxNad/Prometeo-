#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

SAFE_COMMANDS = {
    "git_status": ["git", "status", "--short"],
    "git_branch": ["git", "branch", "--show-current"],
    "git_diff_stat": ["git", "diff", "--stat"],
    "git_diff_cached_stat": ["git", "diff", "--cached", "--stat"],
}


FORBIDDEN_TEXT_MARKERS = (
    ".env",
    "PRIVATE KEY",
    "BEGIN OPENSSH",
    "DATABASE_URL=",
    "PROMETEO_API_KEY=",
    "password",
    "secret",
    "token",
    "specs_finitura",
    "LOCAL_ASSIST_SECRET_MARKER",
    "LOCAL_ASSIST_SPEC_MARKER",
)


def run_safe_command(command: list[str]) -> dict:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": sanitize_text(result.stdout),
        "stderr": sanitize_text(result.stderr),
    }


def sanitize_text(text: str) -> str:
    sanitized_lines = []
    for line in text.splitlines():
        if any(marker.lower() in line.lower() for marker in FORBIDDEN_TEXT_MARKERS):
            sanitized_lines.append("[REDACTED_BY_LOCAL_ASSIST]")
        else:
            sanitized_lines.append(line)
    return "\n".join(sanitized_lines)


def build_context_pack(include_diff_stats: bool = True) -> dict:
    selected = ["git_status", "git_branch"]
    if include_diff_stats:
        selected.extend(["git_diff_stat", "git_diff_cached_stat"])

    return {
        "capability": "LOCAL_ASSIST_BRIDGE_002",
        "mode": "safe_context_pack",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root_label": "PROMETEO_REPO",
        "commands": {
            name: run_safe_command(SAFE_COMMANDS[name])
            for name in selected
        },
        "notes": [
            "Context pack generato solo da comandi allowlist.",
            "Nessuna lettura di .env, secrets, specs_finitura o dati reali.",
            "Output sanificato con marker REDACTED_BY_LOCAL_ASSIST.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build safe PROMETEO local assist context pack")
    parser.add_argument("--no-diff-stats", action="store_true")
    args = parser.parse_args()

    pack = build_context_pack(include_diff_stats=not args.no_diff_stats)
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
