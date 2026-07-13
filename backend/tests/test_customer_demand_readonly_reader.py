from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from app.services.customer_demand_readonly_reader import (
    CustomerDemandReaderInputError,
    read_customer_demand,
)


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
        self.closed = False

    def execute(self, statement, params):
        self.executed.append((statement, params))

    def fetchall(self):
        return deepcopy(self.rows)

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.cursor_instance = FakeCursor(rows)
        self.readonly_calls = []
        self.rollback_calls = 0
        self.close_calls = 0
        self.commit_calls = 0

    def set_session(self, *, readonly, autocommit):
        self.readonly_calls.append((readonly, autocommit))

    def cursor(self):
        return self.cursor_instance

    def rollback(self):
        self.rollback_calls += 1

    def close(self):
        self.close_calls += 1

    def commit(self):
        self.commit_calls += 1
        raise AssertionError("reader must never commit")


def test_reader_uses_one_parameterized_select_and_does_not_mutate():
    rows = [{
        "articolo": "12514",
        "codice_articolo": "7056055000A0",
        "quantita": 94,
        "data_spedizione": None,
        "priorita_cliente": "A",
        "note": "must not be exposed",
    }]
    before = deepcopy(rows)
    connection = FakeConnection(rows)
    retrieved_at = datetime(2026, 7, 13, 10, 0, tzinfo=timezone.utc)

    result = read_customer_demand(
        articolo="12514",
        limit=10,
        connection_factory=lambda: connection,
        now_factory=lambda: retrieved_at,
    )

    assert rows == before
    assert connection.commit_calls == 0
    assert connection.rollback_calls == 1
    assert connection.close_calls == 1
    assert connection.readonly_calls == [(True, False)]
    assert len(connection.cursor_instance.executed) == 1

    statement, params = connection.cursor_instance.executed[0]
    normalized = " ".join(statement.upper().split())
    assert normalized.startswith("SELECT ")
    assert " FROM CUSTOMER_DEMAND " in normalized
    assert all(
        keyword not in normalized
        for keyword in ("INSERT", "UPDATE", "DELETE", "REPLACE", "DROP", "ALTER", "CREATE")
    )
    assert params == ("12514", 10)
    assert set(result["records"][0]) == {
        "articolo", "codice_articolo", "quantita", "data_spedizione", "priorita_cliente"
    }
    assert result["source_status"] == "SOURCE_FOUND"
    assert result["semantic_status"] == "DA_VERIFICARE"
    assert result["confidence"] == "DA_VERIFICARE"
    assert result["freshness"] == "UNKNOWN"
    assert result["runtime_binding"] == "TL_CHAT_READ_ONLY"
    assert result["structural_origin"] == "customer_demand"
    assert result["retrieved_at"] == "2026-07-13T10:00:00+00:00"


def test_reader_returns_source_found_with_empty_records_for_missing_record():
    connection = FakeConnection([])
    result = read_customer_demand(
        codice_articolo="MISSING",
        connection_factory=lambda: connection,
    )
    assert result["source_status"] == "SOURCE_FOUND"
    assert result["records"] == []
    assert result["missing_data"] == ["record_customer_demand_not_found"]
    assert connection.commit_calls == 0


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"articolo": "A", "codice_articolo": "B"}, {"articolo": ""},
     {"articolo": "A", "limit": 0}, {"articolo": "A", "limit": 101}],
)
def test_reader_rejects_invalid_lookup_before_opening_connection(kwargs):
    opened = False

    def factory():
        nonlocal opened
        opened = True
        return FakeConnection([])

    with pytest.raises(CustomerDemandReaderInputError):
        read_customer_demand(connection_factory=factory, **kwargs)

    assert opened is False
