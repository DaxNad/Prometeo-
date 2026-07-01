import json

from backend.app.services.tl_chat_confirmation_evidence_readback import (
    FOUND,
    INVALID,
    INVALID_ARTICLE,
    MISSING,
    REJECTED,
    build_confirmation_evidence_readback,
)


def _write_record(root, filename_article="99999", record_article="99999", **overrides):
    record = {
        "schema": "TL_CHAT_CONFIRMATION_RECORD_V1",
        "article": record_article,
        "confirmation_status": "TL_CONFIRMED_PREVIEW",
        "confidence": "DA_VERIFICARE",
        "requires_persistence_review": True,
        "planner_eligible": False,
        "promoted_to_certo": False,
        "confirmed_fields": ["codice", "disegno", "rev"],
    }
    record.update(overrides)
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{filename_article}_confirmation.json").write_text(
        json.dumps(record),
        encoding="utf-8",
    )


def test_readback_keeps_non_operational_invariants(tmp_path):
    _write_record(tmp_path)

    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is True
    assert result.status == FOUND
    assert result.confidence == "DA_VERIFICARE"
    assert result.requires_confirmation is True
    assert result.requires_persistence_review is True
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False
    assert result.confirmed_fields == ("codice", "disegno", "rev")
    assert "Evidenza TL persistita: presente" in result.rendered_text
    assert "confidence=DA_VERIFICARE" in result.rendered_text
    assert "requires_confirmation=true" in result.rendered_text
    assert "requires_persistence_review=true" in result.rendered_text
    assert "planner_eligible=false" in result.rendered_text
    assert "promoted_to_certo=false" in result.rendered_text
    assert "confirmation evidence is not operational truth" in result.rendered_text


def test_article_specific_schema_is_supported(tmp_path):
    _write_record(
        tmp_path,
        filename_article="88888",
        record_article="88888",
        schema="TL_CHAT_88888_CONFIRMATION_RECORD_V1",
    )

    result = build_confirmation_evidence_readback(
        article="88888",
        confirmation_root=tmp_path,
    )

    assert result.found is True
    assert result.status == FOUND
    assert result.article == "88888"


def test_invalid_schema_is_ignored(tmp_path):
    _write_record(tmp_path, schema="BAD_SCHEMA")

    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == INVALID
    assert result.confidence == "DA_VERIFICARE"
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False


def test_wrong_article_is_ignored(tmp_path):
    _write_record(tmp_path, filename_article="99999", record_article="11111")

    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == INVALID
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False


def test_planner_eligible_true_is_rejected(tmp_path):
    _write_record(tmp_path, planner_eligible=True)

    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == REJECTED
    assert result.confidence == "DA_VERIFICARE"
    assert result.requires_confirmation is True
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False


def test_promoted_to_certo_true_is_rejected(tmp_path):
    _write_record(tmp_path, promoted_to_certo=True)

    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == REJECTED
    assert result.confidence == "DA_VERIFICARE"
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False


def test_missing_evidence_keeps_candidate_only_fallback(tmp_path):
    result = build_confirmation_evidence_readback(
        article="99999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == MISSING
    assert result.confidence == "DA_VERIFICARE"
    assert result.requires_confirmation is True
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False
    assert "candidate-only fallback" in result.rendered_text


def test_invalid_article_code_prevents_file_lookup(tmp_path):
    result = build_confirmation_evidence_readback(
        article="99/999",
        confirmation_root=tmp_path,
    )

    assert result.found is False
    assert result.status == INVALID_ARTICLE
    assert result.confidence == "DA_VERIFICARE"
    assert result.planner_eligible is False
    assert result.promoted_to_certo is False
