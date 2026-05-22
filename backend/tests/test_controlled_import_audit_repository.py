from __future__ import annotations

from copy import deepcopy

from app.repositories.controlled_import_audit_repository import (
    ControlledImportAuditRepository,
)


class _FakeCursor:
    def __init__(self, connection: "_FakeConnection") -> None:
        self.connection = connection
        self._result = None

    def __enter__(self) -> "_FakeCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def execute(self, query: str, params=()) -> None:
        self.connection.queries.append((query, params))
        normalized_query = " ".join(query.split()).lower()
        if normalized_query.startswith("select * from controlled_import_audit_events"):
            if "where audit_event_id" in normalized_query:
                self._result = self.connection.rows_by_audit_id.get(params[0])
            elif "where rollback_id" in normalized_query:
                self._result = [
                    row
                    for row in self.connection.rows_by_audit_id.values()
                    if row.get("rollback_id") == params[0]
                ]
            elif "where confirmation_token_hash" in normalized_query:
                self._result = [
                    row
                    for row in self.connection.rows_by_audit_id.values()
                    if row.get("confirmation_token_hash") == params[0]
                ]
            return

        if normalized_query.startswith("insert into controlled_import_audit_events"):
            row = {
                "audit_event_id": params[0],
                "audit_event_type": params[1],
                "actor": params[2],
                "source": params[3],
                "timestamp_utc": params[4],
                "preview_reference": params[5],
                "dry_run_reference": params[6],
                "confirmation_token_hash": params[7],
                "strong_confirmation_status": params[8],
                "risk_level": params[9],
                "write_mode": params[10],
                "rollback_id": params[11],
                "before_state_hash": params[12],
                "before_state_ref": params[13],
                "after_state_hash": params[14],
                "after_state_ref": params[15],
                "side_effects_summary": params[16],
                "persistence_status": params[17],
                "apply_allowed": params[18],
                "apply_executed": params[19],
                "failure_reason": params[20],
                "created_at": "2026-05-22T00:00:00+00:00",
            }
            self.connection.rows_by_audit_id[row["audit_event_id"]] = row
            self._result = None

    def fetchone(self):
        if isinstance(self._result, list):
            return self._result[0] if self._result else None
        return self._result

    def fetchall(self):
        if self._result is None:
            return []
        if isinstance(self._result, list):
            return self._result
        return [self._result]


class _FakeConnection:
    def __init__(self) -> None:
        self.rows_by_audit_id = {}
        self.queries = []
        self.commits = 0

    def __enter__(self) -> "_FakeConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1


def _valid_event() -> dict:
    return {
        "audit_event_id": "AUDIT-001",
        "audit_event_type": "CONTROLLED_IMPORT_PREVIEW_EVALUATED",
        "actor": "tl-demo",
        "source": "controlled-import-preview",
        "timestamp_utc": "2026-05-22T10:00:00+00:00",
        "preview_reference": "preview-001",
        "dry_run_reference": "dry-run-001",
        "confirmation_token_hash": "sha256:abc123",
        "strong_confirmation_status": "NOT_REQUIRED_FOR_PREVIEW",
        "risk_level": "LOW",
        "write_mode": "PREVIEW_ONLY",
        "rollback_id": "rollback-planned-001",
        "before_state_hash": None,
        "before_state_ref": None,
        "after_state_hash": None,
        "after_state_ref": None,
        "side_effects_summary": {
            "db_write": False,
            "smf_write": False,
            "planner_update": False,
            "file_write": False,
            "external_call": False,
            "ocr": False,
            "ai_runtime": False,
        },
        "persistence_status": "RECORDED",
        "apply_allowed": False,
        "apply_executed": False,
        "failure_reason": None,
    }


def test_controlled_import_audit_repository_records_valid_event():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)

    result = repo.record_event(_valid_event())

    assert result["ok"] is True
    assert result["audit_event_id"] == "AUDIT-001"
    assert result["persistence_status"] == "RECORDED"
    assert result["idempotent_replay"] is False
    assert result["apply_allowed"] is False
    assert result["apply_executed"] is False
    assert connection.commits == 1
    assert "AUDIT-001" in connection.rows_by_audit_id


def test_controlled_import_audit_repository_replays_same_audit_event_id_idempotently():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()

    first = repo.record_event(event)
    second = repo.record_event(event)

    assert first["ok"] is True
    assert second["ok"] is True
    assert second["idempotent_replay"] is True
    assert connection.commits == 1


def test_controlled_import_audit_repository_rejects_duplicate_conflict():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()
    conflict = deepcopy(event)
    conflict["risk_level"] = "MEDIUM"

    repo.record_event(event)
    result = repo.record_event(conflict)

    assert result["ok"] is False
    assert result["error"] == "audit_event_duplicate_conflict"
    assert result["persistence_status"] == "FAILED"
    assert connection.commits == 1


def test_controlled_import_audit_repository_rejects_clear_confirmation_token():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()
    event["confirmation_token"] = "CONFERMO APPLY CONTROLLATO"

    result = repo.record_event(event)

    assert result["ok"] is False
    assert "forbidden_field:confirmation_token" in result["failure_reason"]
    assert connection.commits == 0


def test_controlled_import_audit_repository_rejects_invalid_risk_and_write_mode():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()
    event["risk_level"] = "URGENT"
    event["write_mode"] = "DIRECT_WRITE"

    result = repo.record_event(event)

    assert result["ok"] is False
    assert "invalid_risk_level" in result["failure_reason"]
    assert "invalid_write_mode" in result["failure_reason"]
    assert connection.commits == 0


def test_controlled_import_audit_repository_rejects_invalid_apply_flags():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()
    event["write_mode"] = "APPLY"
    event["apply_executed"] = True
    event["apply_allowed"] = False
    event["strong_confirmation_status"] = "MISSING"

    result = repo.record_event(event)

    assert result["ok"] is False
    assert "invalid_apply_flags" in result["failure_reason"]
    assert "strong_confirmation_required_for_apply" in result["failure_reason"]
    assert connection.commits == 0


def test_controlled_import_audit_repository_finds_events_by_rollback_and_confirmation_hash():
    connection = _FakeConnection()
    repo = ControlledImportAuditRepository(connection_factory=lambda: connection)
    event = _valid_event()
    repo.record_event(event)

    by_rollback = repo.find_by_rollback_id("rollback-planned-001")
    by_confirmation = repo.find_by_confirmation_token_hash("sha256:abc123")

    assert [item["audit_event_id"] for item in by_rollback] == ["AUDIT-001"]
    assert [item["audit_event_id"] for item in by_confirmation] == ["AUDIT-001"]
