#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_MEMORY_DIR = REPO_ROOT / "data" / "local_reports" / "session_memory"
ALLOWED_SUFFIXES = {".md", ".jsonl"}
MAX_OUTPUT_LINES = 200
MAX_FILE_LINES = 32
MAX_LINE_CHARS = 220

FORBIDDEN_PATH_PARTS = {
    ".env",
    "data/local_smf",
    "specs_finitura",
}
FORBIDDEN_SUFFIXES = {
    ".csv",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".xls",
    ".xlsm",
    ".xlsx",
}


def main() -> int:
    args = _parse_args()
    files = _session_files(args.last)

    if not files:
        print("PROMETEO context pack: nessun file sessione trovato in data/local_reports/session_memory/.")
        print("Aggiungi file .md o .jsonl locali; non vengono letti altri percorsi.")
        return 0

    lines: list[str] = [
        "PROMETEO context pack — sintesi locale",
        f"Cartella: data/local_reports/session_memory",
        f"File considerati: {len(files)}",
        "",
    ]

    for file_path in files:
        if len(lines) >= MAX_OUTPUT_LINES:
            lines.append("[OUTPUT_TRUNCATED]")
            break

        lines.extend(_summarize_file(file_path))
        lines.append("")

    print("\n".join(lines[:MAX_OUTPUT_LINES]))
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize local PROMETEO session memory files without external access."
    )
    parser.add_argument(
        "--last",
        type=int,
        default=5,
        help="Number of most recent .md/.jsonl session files to summarize.",
    )
    return parser.parse_args()


def _session_files(limit: int) -> list[Path]:
    if limit <= 0 or not SESSION_MEMORY_DIR.exists():
        return []

    candidates: list[Path] = []
    for path in SESSION_MEMORY_DIR.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        if _is_forbidden_path(path):
            continue
        candidates.append(path)

    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[:limit]


def _is_forbidden_path(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return True

    lowered = relative.lower()
    if any(part in lowered for part in FORBIDDEN_PATH_PARTS):
        return True
    return path.suffix.lower() in FORBIDDEN_SUFFIXES


def _summarize_file(path: Path) -> list[str]:
    relative = path.relative_to(REPO_ROOT).as_posix()
    lines = [f"## {relative}"]

    try:
        if path.suffix.lower() == ".jsonl":
            summary = _summarize_jsonl(path)
        else:
            summary = _summarize_markdown(path)
    except UnicodeDecodeError:
        return lines + ["[SKIPPED: file non testuale]"]
    except OSError as exc:
        return lines + [f"[SKIPPED: {exc.__class__.__name__}]"]

    return lines + summary


def _summarize_markdown(path: Path) -> list[str]:
    output: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("-") or line.startswith("*"):
            output.append(_clip(line))
        elif len(output) < 6:
            output.append(_clip(line))
        if len(output) >= MAX_FILE_LINES:
            output.append("[FILE_TRUNCATED]")
            break

    return output or ["[EMPTY]"]


def _summarize_jsonl(path: Path) -> list[str]:
    output: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            output.append(_clip(line))
        else:
            output.append(_format_jsonl_payload(payload))
        if len(output) >= MAX_FILE_LINES:
            output.append("[FILE_TRUNCATED]")
            break

    return output or ["[EMPTY]"]


def _format_jsonl_payload(payload: object) -> str:
    if not isinstance(payload, dict):
        return _clip(json.dumps(payload, ensure_ascii=True, sort_keys=True))

    preferred_keys = ("timestamp", "phase", "status", "summary", "command", "result")
    parts = []
    for key in preferred_keys:
        value = payload.get(key)
        if value is not None:
            parts.append(f"{key}={value}")

    if not parts:
        parts = [f"{key}={payload[key]}" for key in sorted(payload)[:6]]

    return _clip("; ".join(str(part) for part in parts))


def _clip(value: str) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= MAX_LINE_CHARS:
        return cleaned
    return cleaned[: MAX_LINE_CHARS - 3] + "..."


if __name__ == "__main__":
    raise SystemExit(main())
