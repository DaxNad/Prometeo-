from __future__ import annotations

import sys
from pathlib import Path

from backend.app.memory_retrieval.binding import EvidenceItem, collect_memory_evidence


def _write_memory_file(root: Path, relative: str, front_matter: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter.strip()}\n---\n{body}", encoding="utf-8")
    return path


def _valid_front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_TEST_001",
        "type": "persistent_memory",
        "status": "active",
        "authority": "test_authority",
        "confidence": "DA_VERIFICARE",
        "allowed_for_retrieval": "true",
        "sensitive": "false",
        "last_review": "2026-06-13",
    }
    fields.update(overrides)
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def test_missing_memory_root_returns_empty_list(tmp_path):
    assert collect_memory_evidence(tmp_path / "missing") == []


def test_excludes_file_without_front_matter(tmp_path):
    memory_root = tmp_path / "memory"
    memory_root.mkdir()
    (memory_root / "note.md").write_text("## FATTO\nVisible text", encoding="utf-8")

    assert collect_memory_evidence(memory_root) == []


def test_excludes_file_when_retrieval_not_allowed(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "note.md",
        _valid_front_matter(allowed_for_retrieval="false"),
        "## FATTO\nVisible text",
    )

    assert collect_memory_evidence(memory_root) == []


def test_excludes_sensitive_file(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "note.md",
        _valid_front_matter(sensitive="true"),
        "## FATTO\nVisible text",
    )

    assert collect_memory_evidence(memory_root) == []


def test_extracts_only_allowed_sections(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "note.md",
        _valid_front_matter(),
        (
            "# Note\n"
            "## FATTO\nFact text\n"
            "## INFERENZA\nInference text\n"
            "## DA_VERIFICARE\nVerify text\n"
            "## NON_USARE_COME_FONTE\nForbidden section text\n"
            "## CUSTOM\nCustom text\n"
        ),
    )

    evidence = collect_memory_evidence(memory_root)

    assert [item.section for item in evidence] == ["FATTO", "INFERENZA", "DA_VERIFICARE"]
    assert "Forbidden section text" not in " ".join(item.text for item in evidence)
    assert "Custom text" not in " ".join(item.text for item in evidence)


def test_produces_expected_evidence_fields(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _valid_front_matter(
            memory_id="MEMORY_DOMAIN_TEST",
            type="domain_summary",
            authority="domain_authority",
            confidence="CERTO",
        ),
        "## FATTO\nZAW1 and ZAW2 are distinct.",
    )

    evidence = collect_memory_evidence(memory_root)

    assert evidence == [
        EvidenceItem(
            source_id="MEMORY_DOMAIN_TEST",
            source_path="memory/domain/invariants.md",
            source_type="domain_summary",
            authority="domain_authority",
            confidence="CERTO",
            section="FATTO",
            text="ZAW1 and ZAW2 are distinct.",
            reason="Included FATTO section from retrievable memory file.",
            retrieval_allowed=True,
            sensitive=False,
        )
    ]


def test_filters_by_query_case_insensitive(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "note.md",
        _valid_front_matter(),
        "## FATTO\nAlpha signal\n## INFERENZA\nBeta signal",
    )

    evidence = collect_memory_evidence(memory_root, query="alpha")

    assert len(evidence) == 1
    assert evidence[0].text == "Alpha signal"
    assert collect_memory_evidence(memory_root, query="  ") == collect_memory_evidence(memory_root)


def test_does_not_follow_symlink_outside_memory_root_when_possible(tmp_path):
    memory_root = tmp_path / "memory"
    outside = tmp_path / "outside.md"
    outside.write_text(
        "---\n"
        f"{_valid_front_matter()}\n"
        "---\n"
        "## FATTO\nOutside text",
        encoding="utf-8",
    )
    memory_root.mkdir()
    symlink = memory_root / "outside.md"

    try:
        symlink.symlink_to(outside)
    except OSError:
        return

    assert collect_memory_evidence(memory_root) == []


def test_does_not_import_runtime_modules_or_planner(tmp_path):
    forbidden_modules = (
        "backend.app.api.tl_chat",
        "backend.app.atlas_engine.governed_retrieval",
        "backend.app.services.sequence_planner",
        "backend.app.services.planner_smf",
    )
    for module in forbidden_modules:
        sys.modules.pop(module, None)

    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "note.md",
        _valid_front_matter(),
        "## FATTO\nSafe text",
    )

    collect_memory_evidence(memory_root)

    for module in forbidden_modules:
        assert module not in sys.modules
