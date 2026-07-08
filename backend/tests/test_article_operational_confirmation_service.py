from __future__ import annotations

from datetime import datetime, timezone
import inspect
import json

from app.domain.article_operational_registry import (
    get_operational_registry_entry,
    reset_article_operational_registry_cache,
)
from app.domain.article_tl_summary import build_article_tl_summary
from app.services import article_operational_confirmation_service as service
from app.services.article_operational_confirmation_service import (
    ERROR_AUDIT_NOTE_REQUIRED,
    ERROR_INVALID_ARTICLE,
    ERROR_INVALID_OPERATIONAL_CLASS,
    ERROR_INVALID_PLANNER_ELIGIBLE,
    ERROR_INVALID_TL_CONFIRMATION_REQUIRED,
    ERROR_UNAUTHORIZED_AUTHORITY,
    ERROR_WRITE_FAILED,
    ERROR_WRITE_SUCCEEDED_READBACK_FAILED,
    confirm_article_operational_status,
)


def _write_registry(path, payload=None):
    payload = payload or {
        "version": "test",
        "purpose": "temporary registry",
        "rule": "test rule",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "classes": {
            "STANDARD": "Codice ordinario pianificabile.",
            "REFERENCE_ONLY": "Codice consultabile.",
        },
        "articles": {
            "EXIST1": {
                "article": "EXIST1",
                "description": "existing",
                "operational_class": "REFERENCE_ONLY",
                "planner_eligible": False,
                "tl_confirmation_required": True,
                "unrelated_field": "preserve-me",
            }
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _confirm(**overrides):
    payload = {
        "article": "NEW01",
        "operational_class": "STANDARD",
        "planner_eligible": True,
        "tl_confirmation_required": False,
        "authority_role": "RESPONSABILE_PRODUZIONE",
        "audit_note": "Conferma operativa umana.",
        "confirmed_at": "2026-07-08T10:00:00+00:00",
        "material": "MAT-01",
        "drawing": "DRAW-01",
        "description": "Nuovo articolo confermato",
    }
    payload.update(overrides)
    return confirm_article_operational_status(**payload)


def test_confirm_operational_status_creates_article_and_readback(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    original = _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    result = _confirm()

    assert result.ok is True
    assert result.article == "NEW01"
    assert result.created is True
    assert result.updated is False
    assert result.previous_record is None
    assert result.registry_path == str(registry_path)
    assert result.confirmed_at == "2026-07-08T10:00:00+00:00"
    assert result.current_record["operational_class"] == "STANDARD"
    assert result.current_record["planner_eligible"] is True
    assert result.current_record["tl_confirmation_required"] is False
    assert result.current_record["source"] == "human_operational_confirmation"
    assert result.current_record["source_authority"] == "RESPONSABILE_PRODUZIONE"
    assert result.current_record["confirmation_origin"] == "HUMAN_EXPLICIT_CONFIRMATION"

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    assert stored["version"] == original["version"]
    assert stored["rule"] == original["rule"]
    assert stored["classes"] == original["classes"]
    assert stored["articles"]["EXIST1"] == original["articles"]["EXIST1"]
    assert stored["updated_at"] == "2026-07-08T10:00:00+00:00"

    readback = get_operational_registry_entry("new01")
    assert readback is not None
    assert readback["operational_class"] == "STANDARD"

    summary = build_article_tl_summary("NEW01")
    assert summary["ok"] is True
    assert summary["operational_class"] == "STANDARD"


def test_confirm_operational_status_updates_existing_and_preserves_fields(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    result = _confirm(
        article="EXIST1",
        operational_class="STANDARD",
        planner_eligible=True,
        audit_note="Cambio stato confermato.",
        description=None,
    )

    assert result.ok is True
    assert result.created is False
    assert result.updated is True
    assert result.previous_record["operational_class"] == "REFERENCE_ONLY"
    assert result.current_record["operational_class"] == "STANDARD"
    assert result.current_record["unrelated_field"] == "preserve-me"
    assert result.current_record["description"] == "existing"
    assert result.current_record["confirmation_history"] == [
        {
            "operational_class": "REFERENCE_ONLY",
            "planner_eligible": False,
            "tl_confirmation_required": True,
            "description": "existing",
            "superseded_at": "2026-07-08T10:00:00+00:00",
            "superseded_by_authority": "RESPONSABILE_PRODUZIONE",
        }
    ]


def test_confirm_operational_status_is_idempotent_for_same_confirmation(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    first = _confirm()
    before = registry_path.read_text(encoding="utf-8")
    second = _confirm()
    after = registry_path.read_text(encoding="utf-8")

    assert first.ok is True
    assert second.ok is True
    assert second.created is False
    assert second.updated is False
    assert before == after
    assert second.persisted is False


def test_confirm_operational_status_is_idempotent_without_explicit_timestamp(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    first = _confirm(confirmed_at=None)
    before = registry_path.read_text(encoding="utf-8")
    stored_before = json.loads(before)
    reset_calls = 0

    def count_reset():
        nonlocal reset_calls
        reset_calls += 1

    monkeypatch.setattr(service, "reset_article_operational_registry_cache", count_reset)

    second = _confirm(confirmed_at=None)
    after = registry_path.read_text(encoding="utf-8")
    stored_after = json.loads(after)

    assert first.ok is True
    assert second.ok is True
    assert second.created is False
    assert second.updated is False
    assert second.persisted is False
    assert before == after
    assert stored_after["updated_at"] == stored_before["updated_at"]
    assert (
        stored_after["articles"]["NEW01"]["confirmed_at"]
        == stored_before["articles"]["NEW01"]["confirmed_at"]
    )
    assert "confirmation_history" not in stored_after["articles"]["NEW01"]
    assert reset_calls == 0


def test_confirm_operational_status_noops_when_only_audit_note_changes(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    first = _confirm()
    before = registry_path.read_text(encoding="utf-8")
    second = _confirm(audit_note="Nuova nota senza variazione operativa.")
    after = registry_path.read_text(encoding="utf-8")

    assert first.ok is True
    assert second.ok is True
    assert second.updated is False
    assert before == after
    assert second.current_record["audit_note"] == "Conferma operativa umana."


def test_confirm_operational_status_rejects_invalid_class_without_write(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(operational_class="NOT_A_CLASS")

    assert result.ok is False
    assert result.error_code == ERROR_INVALID_OPERATIONAL_CLASS
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_rejects_unauthorized_role_without_write(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(authority_role="TL")

    assert result.ok is False
    assert result.error_code == ERROR_UNAUTHORIZED_AUTHORITY
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_rejects_empty_article_without_write(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(article="")

    assert result.ok is False
    assert result.error_code == ERROR_INVALID_ARTICLE
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_rejects_non_bool_planner_without_write(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(planner_eligible="true")

    assert result.ok is False
    assert result.error_code == ERROR_INVALID_PLANNER_ELIGIBLE
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_rejects_non_bool_tl_confirmation_without_write(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(tl_confirmation_required="false")

    assert result.ok is False
    assert result.error_code == ERROR_INVALID_TL_CONFIRMATION_REQUIRED
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_requires_audit_note_for_significant_update(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(
        article="EXIST1",
        operational_class="STANDARD",
        planner_eligible=True,
        audit_note="",
    )

    assert result.ok is False
    assert result.error_code == ERROR_AUDIT_NOTE_REQUIRED
    assert result.previous_record["operational_class"] == "REFERENCE_ONLY"
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_requires_audit_note_for_creation(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm(audit_note="")

    assert result.ok is False
    assert result.error_code == ERROR_AUDIT_NOTE_REQUIRED
    assert registry_path.read_text(encoding="utf-8") == before


def test_confirm_operational_status_atomic_write_failure_preserves_file_and_cache(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    before = registry_path.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()
    assert get_operational_registry_entry("NEW01") is None

    def failing_write(_path, _data):
        raise OSError("disk full")

    monkeypatch.setattr(service, "_atomic_write_json", failing_write)

    result = _confirm()

    assert result.ok is False
    assert result.error_code == ERROR_WRITE_FAILED
    assert result.persisted is False
    assert registry_path.read_text(encoding="utf-8") == before
    assert get_operational_registry_entry("NEW01") is None


def test_confirm_operational_status_invalidates_cache_after_success(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()
    assert get_operational_registry_entry("NEW01") is None

    result = _confirm()

    assert result.ok is True
    assert result.persisted is True
    assert get_operational_registry_entry("NEW01") is not None


def test_confirm_operational_status_readback_failure_is_distinguishable_after_write(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()
    monkeypatch.setattr(service, "get_operational_registry_entry", lambda _code: None)

    result = _confirm(article="EXIST1", audit_note="Cambio con readback fallito.")

    assert result.ok is False
    assert result.error_code == ERROR_WRITE_SUCCEEDED_READBACK_FAILED
    assert result.persisted is True
    assert result.current_record["operational_class"] == "STANDARD"
    assert result.registry_path == str(registry_path)
    assert result.confirmed_at == "2026-07-08T10:00:00+00:00"

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    record = stored["articles"]["EXIST1"]
    assert record["operational_class"] == "STANDARD"
    assert record["confirmation_history"][0]["operational_class"] == "REFERENCE_ONLY"


def test_confirm_operational_status_does_not_modify_other_sources(tmp_path, monkeypatch):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    preview_file = tmp_path / "12514_metadata_preview.json"
    confirmation_file = tmp_path / "12514_confirmation.json"
    preview_file.write_text('{"status":"PREVIEW_ONLY"}\n', encoding="utf-8")
    confirmation_file.write_text('{"confidence":"DA_VERIFICARE"}\n', encoding="utf-8")
    preview_before = preview_file.read_text(encoding="utf-8")
    confirmation_before = confirmation_file.read_text(encoding="utf-8")
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))

    result = _confirm()

    assert result.ok is True
    assert preview_file.read_text(encoding="utf-8") == preview_before
    assert confirmation_file.read_text(encoding="utf-8") == confirmation_before


def test_confirm_operational_status_second_update_preserves_history_order(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    first = _confirm(
        article="EXIST1",
        operational_class="STANDARD",
        planner_eligible=True,
        tl_confirmation_required=False,
        audit_note="A to B.",
        confirmed_at="2026-07-08T10:00:00+00:00",
        description=None,
    )
    second = _confirm(
        article="EXIST1",
        operational_class="RICAMBIO",
        planner_eligible=False,
        tl_confirmation_required=True,
        audit_note="B to C.",
        confirmed_at="2026-07-08T11:00:00+00:00",
        description=None,
    )

    assert first.ok is True
    assert second.ok is True
    history = second.current_record["confirmation_history"]
    assert [item["operational_class"] for item in history] == [
        "REFERENCE_ONLY",
        "STANDARD",
    ]
    assert all("confirmation_history" not in item for item in history)
    assert history[0]["superseded_at"] == "2026-07-08T10:00:00+00:00"
    assert history[1]["superseded_at"] == "2026-07-08T11:00:00+00:00"


def test_confirm_operational_status_idempotent_update_does_not_duplicate_history(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    first = _confirm(article="EXIST1", audit_note="A to B.", description=None)
    before = registry_path.read_text(encoding="utf-8")
    second = _confirm(
        article="EXIST1",
        audit_note="Ignored no-op note.",
        confirmed_at="2026-07-08T11:00:00+00:00",
        description=None,
    )
    after = registry_path.read_text(encoding="utf-8")

    assert first.ok is True
    assert second.ok is True
    assert second.updated is False
    assert before == after
    assert len(second.current_record["confirmation_history"]) == 1


def test_confirm_operational_status_updates_legacy_record_without_history(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "article_operational_registry.json"
    _write_registry(registry_path)
    monkeypatch.setenv("OPERATIONAL_REGISTRY_PATH", str(registry_path))
    reset_article_operational_registry_cache()

    result = _confirm(article="EXIST1", audit_note="Legacy update.", description=None)

    assert result.ok is True
    assert result.current_record["unrelated_field"] == "preserve-me"
    assert result.current_record["confirmation_history"][0]["operational_class"] == "REFERENCE_ONLY"
    assert "authority_role" not in result.current_record["confirmation_history"][0]


def test_contract_documents_planner_eligible_limits():
    text = (
        "docs/ARTICLE_OPERATIONAL_CONFIRMATION_SERVICE_CONTRACT_001.md"
    )
    from pathlib import Path

    content = Path(text).read_text(encoding="utf-8")
    assert "planner_eligible=true" in content
    assert "ordine autorizzato" in content
    assert "quantità autorizzata" in content
    assert "turno autorizzato" in content
    assert "sequenziamento autorizzato" in content
    assert "avvio automatico della produzione" in content
    assert "Idempotenza Sostanziale" in content
    assert "Confirmation History" in content
    assert "Readback Fallito" in content


def test_confirmation_service_is_generic_and_does_not_hardcode_12514():
    assert "12514" not in inspect.getsource(service.confirm_article_operational_status)
