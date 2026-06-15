from __future__ import annotations

import sys
from pathlib import Path

from backend.app.memory_retrieval.binding import collect_memory_evidence


def _write_memory_file(root: Path, relative: str, front_matter: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter.strip()}\n---\n{body}", encoding="utf-8")
    return path


def _front_matter(**overrides: str) -> str:
    fields = {
        "memory_id": "MEMORY_EVAL_001",
        "type": "domain_invariant",
        "status": "active",
        "authority": "governed_memory",
        "confidence": "CERTO",
        "allowed_for_retrieval": "true",
        "sensitive": "false",
        "last_review": "2026-06-13",
    }
    fields.update(overrides)
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def test_eval_domain_zaw_query_returns_relevant_evidence(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(
            memory_id="MEMORY_DOMAIN_INVARIANTS",
            authority="governed_memory",
            confidence="CERTO",
        ),
        "## FATTO\nZAW1 e ZAW2 non sono intercambiabili.",
    )

    evidence = collect_memory_evidence(memory_root, query="ZAW2")

    assert len(evidence) >= 1
    item = evidence[0]
    assert item.source_id == "MEMORY_DOMAIN_INVARIANTS"
    assert item.section == "FATTO"
    assert item.confidence == "CERTO"
    assert item.authority == "governed_memory"
    assert "ZAW2" in item.text
    assert item.sensitive is False
    assert item.retrieval_allowed is True


def test_eval_noise_sections_are_excluded(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(),
        (
            "## FATTO\nZAW1 e ZAW2 restano distinti.\n"
            "## NON_USARE_COME_FONTE\nRUMORE_NON_AUTORIZZATO\n"
            "## CUSTOM\nALTRO_RUMORE_NON_AUTORIZZATO\n"
        ),
    )

    evidence = collect_memory_evidence(memory_root)
    text = "\n".join(item.text for item in evidence)

    assert [item.section for item in evidence] == ["FATTO"]
    assert "RUMORE_NON_AUTORIZZATO" not in text
    assert "ALTRO_RUMORE_NON_AUTORIZZATO" not in text


def test_eval_query_is_case_insensitive(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/invariants.md",
        _front_matter(),
        "## FATTO\nZAW2 richiede evidenza esplicita.",
    )

    lower = collect_memory_evidence(memory_root, query="zaw2")
    mixed = collect_memory_evidence(memory_root, query="ZaW2")

    assert lower
    assert lower == mixed


def test_eval_confidence_is_not_promoted(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/check.md",
        _front_matter(confidence="DA_VERIFICARE"),
        "## FATTO\nAffermazione operativa da verificare prima dell'uso.",
    )

    evidence = collect_memory_evidence(memory_root)

    assert len(evidence) == 1
    assert evidence[0].confidence == "DA_VERIFICARE"
    assert evidence[0].confidence != "CERTO"


def test_eval_authority_is_preserved_per_file(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "a/governed.md",
        _front_matter(memory_id="MEMORY_AUTH_A", authority="governed_memory"),
        "## FATTO\nEvidenza da memoria governata.",
    )
    _write_memory_file(
        memory_root,
        "b/tl.md",
        _front_matter(memory_id="MEMORY_AUTH_B", authority="tl_confirmed_summary"),
        "## FATTO\nEvidenza da sintesi confermata TL.",
    )

    evidence = collect_memory_evidence(memory_root)

    assert {item.source_id: item.authority for item in evidence} == {
        "MEMORY_AUTH_A": "governed_memory",
        "MEMORY_AUTH_B": "tl_confirmed_summary",
    }


def test_eval_order_is_stable_between_calls(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "b/second.md",
        _front_matter(memory_id="MEMORY_ORDER_B"),
        "## FATTO\nSecondo path.\n## INFERENZA\nSeconda sezione.",
    )
    _write_memory_file(
        memory_root,
        "a/first.md",
        _front_matter(memory_id="MEMORY_ORDER_A"),
        "## FATTO\nPrimo path.",
    )

    first = collect_memory_evidence(memory_root)
    second = collect_memory_evidence(memory_root)

    assert first == second
    assert [(item.source_path, item.section) for item in first] == [
        ("memory/a/first.md", "FATTO"),
        ("memory/b/second.md", "FATTO"),
        ("memory/b/second.md", "INFERENZA"),
    ]


def test_eval_excludes_retrieval_not_allowed(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/private.md",
        _front_matter(allowed_for_retrieval="false", sensitive="false"),
        "## FATTO\nTesto non autorizzato al retrieval.",
    )

    assert collect_memory_evidence(memory_root) == []


def test_eval_excludes_sensitive_file(tmp_path):
    memory_root = tmp_path / "memory"
    _write_memory_file(
        memory_root,
        "domain/sensitive.md",
        _front_matter(allowed_for_retrieval="true", sensitive="true"),
        "## FATTO\nTesto sensibile.",
    )

    assert collect_memory_evidence(memory_root) == []


def test_eval_does_not_import_runtime_modules_or_planner(tmp_path):
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
        "domain/invariants.md",
        _front_matter(),
        "## FATTO\nEvidenza isolata.",
    )

    collect_memory_evidence(memory_root)

    for module in forbidden_modules:
        assert module not in sys.modules
