from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MEMORY_ROOT = ROOT / "memory"

REQUIRED_MEMORY_FILES = (
    Path("memory/README_MEMORY.md"),
    Path("memory/index.md"),
    Path("memory/active_context.md"),
    Path("memory/project_state.md"),
    Path("memory/domain/invariants.md"),
    Path("memory/capabilities/capability_status.md"),
    Path("memory/retrieval/retrieval_policy.md"),
)

REQUIRED_FRONT_MATTER_KEYS = {
    "memory_id",
    "type",
    "status",
    "authority",
    "confidence",
    "allowed_for_retrieval",
    "sensitive",
    "last_review",
}

REQUIRED_SECTIONS = (
    "## FATTO",
    "## INFERENZA",
    "## DA_VERIFICARE",
)

FORBIDDEN_MARKERS = (
    "PRIVATE KEY",
    "SECRET=",
    "TOKEN=",
    "DATABASE_URL=",
    ".env=",
    "specs_finitura/",
    "data/local_smf",
    ".xlsx",
    ".xls",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
)


def _memory_markdown_files() -> list[Path]:
    return sorted(MEMORY_ROOT.rglob("*.md"))


def _read_repo_file(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _front_matter(text: str, path: Path) -> dict[str, str]:
    lines = text.splitlines()
    assert lines, f"{path} is empty"
    assert lines[0] == "---", f"{path} missing YAML front matter start"

    try:
        end_index = lines[1:].index("---") + 1
    except ValueError as exc:
        raise AssertionError(f"{path} missing YAML front matter end") from exc

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        assert separator == ":", f"{path} has invalid front matter line: {line}"
        fields[key.strip()] = value.strip()

    return fields


def test_required_memory_files_exist():
    for path in REQUIRED_MEMORY_FILES:
        assert (ROOT / path).is_file(), f"missing required memory file: {path}"


def test_every_memory_markdown_file_has_yaml_front_matter():
    files = _memory_markdown_files()
    assert files, "memory must contain markdown files"

    for path in files:
        _front_matter(path.read_text(encoding="utf-8"), path.relative_to(ROOT))


def test_every_memory_front_matter_has_required_fields():
    for path in _memory_markdown_files():
        fields = _front_matter(path.read_text(encoding="utf-8"), path.relative_to(ROOT))
        assert REQUIRED_FRONT_MATTER_KEYS <= set(fields), (
            f"{path.relative_to(ROOT)} missing front matter fields: "
            f"{sorted(REQUIRED_FRONT_MATTER_KEYS - set(fields))}"
        )


def test_retrievable_memory_is_not_sensitive():
    for path in _memory_markdown_files():
        fields = _front_matter(path.read_text(encoding="utf-8"), path.relative_to(ROOT))
        allowed = fields["allowed_for_retrieval"].lower()
        sensitive = fields["sensitive"].lower()

        if allowed == "true":
            assert sensitive == "false", (
                f"{path.relative_to(ROOT)} is retrievable but sensitive={fields['sensitive']}"
            )


def test_required_memory_files_have_required_sections():
    for path in REQUIRED_MEMORY_FILES:
        text = _read_repo_file(path)
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{path} missing section {section}"


def test_memory_files_do_not_contain_forbidden_markers():
    for path in _memory_markdown_files():
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_MARKERS:
            assert marker not in text, f"{path.relative_to(ROOT)} contains forbidden marker {marker}"


def test_memory_index_lists_all_required_memory_files():
    index_text = _read_repo_file(Path("memory/index.md"))
    for path in REQUIRED_MEMORY_FILES:
        assert str(path) in index_text, f"memory/index.md does not list {path}"
