from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatternExample:
    path: str
    title: str
    status: str
    content: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _pattern_examples_dir() -> Path:
    return _repo_root() / "docs" / "pattern_registry" / "examples"


def _extract_title(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "UNTITLED_PATTERN"


def _extract_status(content: str) -> str:
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "## STATUS":
            for next_line in lines[idx + 1:]:
                value = next_line.strip()
                if value:
                    return value
    return "UNKNOWN"


def load_pattern_examples() -> list[PatternExample]:
    base = _pattern_examples_dir()
    if not base.exists():
        return []

    patterns: list[PatternExample] = []
    for path in sorted(base.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        patterns.append(
            PatternExample(
                path=str(path.relative_to(_repo_root())),
                title=_extract_title(content),
                status=_extract_status(content),
                content=content,
            )
        )
    return patterns


def list_patterns() -> list[dict[str, str]]:
    return [
        {
            "path": p.path,
            "title": p.title,
            "status": p.status,
        }
        for p in load_pattern_examples()
    ]


def _extract_field(content: str, field_name: str) -> str:
    prefix = f"{field_name}:"
    for line in content.splitlines():
        if line.strip().lower().startswith(prefix.lower()):
            return line.split(":", 1)[1].strip()
    return ""


def find_patterns_by_station(station: str) -> list[PatternExample]:
    needle = station.strip().lower()
    if not needle:
        return []
    return [
        p for p in load_pattern_examples()
        if needle in _extract_field(p.content, "Postazione/i").lower()
    ]


def find_patterns_by_code(code: str) -> list[PatternExample]:
    needle = code.strip().lower()
    if not needle:
        return []
    return [
        p for p in load_pattern_examples()
        if needle in _extract_field(p.content, "Codice/i").lower()
    ]
