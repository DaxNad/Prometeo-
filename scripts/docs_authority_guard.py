#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MASTER_DOC = Path("docs/PROMETEO_MASTER.md")
MASTER_REFERENCES = ("docs/PROMETEO_MASTER.md", "PROMETEO_MASTER.md")
DOC_ROOTS = ("docs",)
EXTRA_MARKDOWN = ("README.md", "AGENTS.md", "CLAUDE.md")

AUTHORITY_PATTERNS = (
    "regola permanente",
    "source of truth",
    "fonte primaria",
    "must always",
    "vincolo permanente",
)
AUTHORITY_RE = re.compile(
    "|".join(re.escape(pattern) for pattern in AUTHORITY_PATTERNS),
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AuthorityViolation:
    path: Path
    line: int
    pattern: str
    text: str


def _repo_path(path: Path) -> Path:
    try:
        return path.resolve().relative_to(ROOT)
    except ValueError:
        return path


def _is_markdown(path: Path) -> bool:
    return path.suffix.lower() == ".md"


def _is_guarded_doc(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return path.name != MASTER_DOC.name

    if rel == MASTER_DOC:
        return False
    if str(rel) in EXTRA_MARKDOWN:
        return True
    return rel.parts[:1] in tuple((root,) for root in DOC_ROOTS)


def discover_changed_markdown() -> list[Path]:
    paths: set[Path] = set()
    commands = (
        ("git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD", "--", "*.md"),
        ("git", "ls-files", "--others", "--exclude-standard", "--", "*.md"),
    )

    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            continue

        for line in result.stdout.splitlines():
            rel = Path(line.strip())
            if rel:
                paths.add(ROOT / rel)

    return sorted(path for path in paths if _is_markdown(path) and _is_guarded_doc(path))


def discover_all_markdown() -> list[Path]:
    paths: list[Path] = []
    for root in DOC_ROOTS:
        paths.extend((ROOT / root).rglob("*.md"))
    for extra in EXTRA_MARKDOWN:
        path = ROOT / extra
        if path.exists():
            paths.append(path)
    return sorted(path for path in paths if _is_guarded_doc(path))


def scan_markdown(paths: Iterable[Path]) -> list[AuthorityViolation]:
    violations: list[AuthorityViolation] = []
    for path in paths:
        if not path.exists() or not _is_markdown(path) or not _is_guarded_doc(path):
            continue

        text = path.read_text(encoding="utf-8")
        if any(reference in text for reference in MASTER_REFERENCES):
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            match = AUTHORITY_RE.search(line)
            if match:
                violations.append(
                    AuthorityViolation(
                        path=_repo_path(path),
                        line=line_number,
                        pattern=match.group(0),
                        text=line.strip(),
                    )
                )
    return violations


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Block new permanent authority rules outside docs/PROMETEO_MASTER.md "
            "unless they explicitly reference the Master."
        )
    )
    parser.add_argument("paths", nargs="*", help="Specific markdown files to scan.")
    parser.add_argument("--all", action="store_true", help="Scan all guarded markdown files.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(argv or sys.argv[1:]))

    if args.paths:
        paths = [ROOT / path for path in args.paths]
        mode = "explicit"
    elif args.all:
        paths = discover_all_markdown()
        mode = "all"
    else:
        paths = discover_changed_markdown()
        mode = "changed"

    violations = scan_markdown(paths)
    if violations:
        print("[PROMETEO DOCS AUTHORITY GUARD] FAIL")
        print("Permanent authority wording outside PROMETEO_MASTER.md requires an explicit Master reference.")
        for item in violations:
            print(f"- {item.path}:{item.line}: {item.pattern!r} :: {item.text}")
        return 1

    print(f"[PROMETEO DOCS AUTHORITY GUARD] OK mode={mode} files={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
