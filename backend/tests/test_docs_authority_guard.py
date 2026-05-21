from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "docs_authority_guard.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("docs_authority_guard", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_docs_authority_guard_blocks_strong_rule_without_master_reference(tmp_path):
    guard = _load_guard_module()
    doc = tmp_path / "docs" / "fragment.md"
    doc.parent.mkdir()
    doc.write_text("Questa e una regola permanente del sistema.\n", encoding="utf-8")

    violations = guard.scan_markdown([doc])

    assert len(violations) == 1
    assert violations[0].pattern.lower() == "regola permanente"


def test_docs_authority_guard_allows_strong_rule_with_master_reference(tmp_path):
    guard = _load_guard_module()
    doc = tmp_path / "docs" / "linked.md"
    doc.parent.mkdir()
    doc.write_text(
        "Fonte primaria: docs/PROMETEO_MASTER.md\n"
        "Questa nota cita source of truth solo come rimando al Master.\n",
        encoding="utf-8",
    )

    assert guard.scan_markdown([doc]) == []


def test_docs_authority_guard_ignores_master_doc(tmp_path, monkeypatch):
    guard = _load_guard_module()
    fake_root = tmp_path
    master = fake_root / "docs" / "PROMETEO_MASTER.md"
    master.parent.mkdir()
    master.write_text("vincolo permanente ammesso nel Master.\n", encoding="utf-8")

    monkeypatch.setattr(guard, "ROOT", fake_root)

    assert guard.scan_markdown([master]) == []
