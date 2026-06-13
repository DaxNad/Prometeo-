from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_FRONT_MATTER_FIELDS = frozenset(
    {
        "memory_id",
        "type",
        "status",
        "authority",
        "confidence",
        "allowed_for_retrieval",
        "sensitive",
        "last_review",
    }
)

ALLOWED_SECTIONS = ("FATTO", "INFERENZA", "DA_VERIFICARE")

FORBIDDEN_PATH_MARKERS = (
    ".env",
    "specs_finitura",
    "data/local_smf",
    ".xlsx",
    ".xls",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
)


@dataclass(frozen=True)
class EvidenceItem:
    source_id: str
    source_path: str
    source_type: str
    authority: str
    confidence: str
    section: str
    text: str
    reason: str
    retrieval_allowed: bool
    sensitive: bool


def collect_memory_evidence(memory_root: Path, query: str | None = None) -> list[EvidenceItem]:
    root = memory_root.resolve(strict=False)
    if not root.is_dir():
        return []

    normalized_query = (query or "").strip().lower()
    evidence: list[EvidenceItem] = []

    for path in sorted(root.rglob("*.md")):
        safe_path = _safe_markdown_path(path, root)
        if safe_path is None:
            continue

        try:
            text = safe_path.read_text(encoding="utf-8")
        except OSError:
            continue

        front_matter = _parse_front_matter(text)
        if front_matter is None:
            continue

        if not _front_matter_allows_retrieval(front_matter):
            continue

        relative_path = safe_path.relative_to(root).as_posix()
        source_path = f"memory/{relative_path}"
        if _contains_forbidden_marker(source_path):
            continue

        for section, section_text in _extract_allowed_sections(text):
            reason = f"Included {section} section from retrievable memory file."
            if normalized_query and normalized_query not in section_text.lower() and normalized_query not in reason.lower():
                continue

            evidence.append(
                EvidenceItem(
                    source_id=front_matter["memory_id"],
                    source_path=source_path,
                    source_type=front_matter["type"],
                    authority=front_matter["authority"],
                    confidence=front_matter["confidence"],
                    section=section,
                    text=section_text,
                    reason=reason,
                    retrieval_allowed=True,
                    sensitive=False,
                )
            )

    return evidence


def _safe_markdown_path(path: Path, root: Path) -> Path | None:
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        return None

    if not resolved.is_file():
        return None

    if _contains_forbidden_marker(resolved.as_posix()):
        return None

    try:
        resolved.relative_to(root)
    except ValueError:
        return None

    return resolved


def _contains_forbidden_marker(value: str) -> bool:
    normalized = value.lower()
    return any(marker.lower() in normalized for marker in FORBIDDEN_PATH_MARKERS)


def _parse_front_matter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None

    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return None

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if separator != ":":
            return None
        fields[key.strip()] = value.strip()

    return fields


def _front_matter_allows_retrieval(front_matter: dict[str, str]) -> bool:
    if not REQUIRED_FRONT_MATTER_FIELDS <= set(front_matter):
        return False

    if any(not str(front_matter[field]).strip() for field in REQUIRED_FRONT_MATTER_FIELDS):
        return False

    if front_matter["allowed_for_retrieval"].strip().lower() != "true":
        return False

    if front_matter["sensitive"].strip().lower() != "false":
        return False

    return True


def _extract_allowed_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_section: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_section is not None:
                _append_section(sections, current_section, current_lines)

            heading = line[3:].strip()
            current_section = heading if heading in ALLOWED_SECTIONS else None
            current_lines = []
            continue

        if current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        _append_section(sections, current_section, current_lines)

    return sections


def _append_section(sections: list[tuple[str, str]], section: str, lines: list[str]) -> None:
    text = "\n".join(lines).strip()
    if text:
        sections.append((section, text))
