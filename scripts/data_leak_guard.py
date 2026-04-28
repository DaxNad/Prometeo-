#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BLOCKED_FILE_SUFFIXES = {
    ".xlsx", ".xls", ".xlsm",
    ".pdf",
    ".png", ".jpg", ".jpeg", ".heic", ".webp", ".tif", ".tiff",
    ".zip", ".7z", ".rar", ".tar", ".gz",
    ".db", ".sqlite", ".sqlite3",
    ".dump", ".backup", ".bak",
    ".log",
}

ALLOWED_FILE_EXCEPTIONS = {
    "docs/backend_legacy_ui/apple-touch-icon.png",
    "docs/backend_legacy_ui/favicon.png",
    "docs/backend_legacy_ui/icon-192.png",
    "docs/backend_legacy_ui/icon-512.png",
    "frontend_legacy/apple-touch-icon.png",
}

ALLOWED_SUFFIX_DIRS = {
    "backend/sql": {".sql"},
}

BLOCKED_PATH_TOKENS = {
    "/Users/",
    "/private/var/mobile",
    "davidepiangiolino",
    "Documents/PROMETEO",
    "Documents/local_smf",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)(postgresql|postgres|mysql|mongodb)://(?!localhost/|127\\.0\\.0\\.1/)[^\\s'\"<>]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\\-]{20,}"),
]

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

ALLOWED_EMAIL_EXCEPTIONS = set()

TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".txt", ".yml", ".yaml",
    ".json", ".toml", ".sh", ".sql",
    ".html", ".css",
}


def git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def tracked_files() -> list[str]:
    return git_lines(["ls-files"])


def is_allowed_suffix_dir(path: str, suffix: str) -> bool:
    for root, suffixes in ALLOWED_SUFFIX_DIRS.items():
        if path.startswith(root + "/") and suffix in suffixes:
            return True
    return False


def scan_file_paths(files: list[str]) -> list[str]:
    violations = []

    for path in files:
        p = Path(path)
        suffix = p.suffix.lower()

        if path in ALLOWED_FILE_EXCEPTIONS:
            continue

        if is_allowed_suffix_dir(path, suffix):
            continue

        if suffix in BLOCKED_FILE_SUFFIXES:
            violations.append(f"blocked_file:{path}")
            continue

        for token in BLOCKED_PATH_TOKENS:
            if token in path:
                violations.append(f"blocked_path:{path}")
                break

    return violations


def scan_text_content(files: list[str]) -> list[str]:
    violations = []

    self_file = "scripts/data_leak_guard.py"

    for path in files:
        if path == self_file:
            continue

        p = Path(path)
        suffix = p.suffix.lower()

        if suffix not in TEXT_SUFFIXES:
            continue

        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue

        for idx, line in enumerate(text.splitlines(), start=1):
            if any(token in line for token in BLOCKED_PATH_TOKENS):
                violations.append(f"blocked_local_path:{path}:{idx}")
                continue

            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    violations.append(f"possible_secret:{path}:{idx}")
                    break

            for match in EMAIL_PATTERN.findall(line):
                if match not in ALLOWED_EMAIL_EXCEPTIONS:
                    violations.append(f"possible_email:{path}:{idx}:{match}")

    return violations


def main() -> int:
    files = tracked_files()

    violations = []
    violations.extend(scan_file_paths(files))
    violations.extend(scan_text_content(files))

    if violations:
        print("[PROMETEO DATA LEAK GUARD] REPOSITORY VIOLATION")
        print("Rilevati possibili dati sensibili o file non ammessi nel repo.")
        print("")
        for v in violations:
            print(f" - {v}")
        print("")
        print("Azione richiesta: rimuovere, anonimizzare o aggiungere eccezione esplicita motivata.")
        return 1

    print("[PROMETEO DATA LEAK GUARD] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
