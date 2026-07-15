from __future__ import annotations

import sqlite3
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import tl_chat as tl_chat_api
from app.main import app
from app.services.customer_demand_context_resolver_binding import (
    resolve_customer_demand_context,
)
from app.services.customer_demand_readonly_reader import read_customer_demand
from app.services.customer_demand_runtime_authorization import (
    authorize_customer_demand_runtime,
)


ARTICLE = "SYNTH-CD-001"


class InMemoryCustomerDemandDatabase:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.uri = f"file:customer-demand-{uuid4().hex}?mode=memory&cache=shared"
        self.anchor = sqlite3.connect(self.uri, uri=True)
        self.anchor.execute(
            """
            CREATE TABLE customer_demand (
                id INTEGER PRIMARY KEY,
                articolo TEXT NOT NULL,
                codice_articolo TEXT,
                quantita INTEGER,
                data_spedizione DATE,
                priorita_cliente TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.anchor.execute(
            """
            INSERT INTO customer_demand (
                articolo,
                codice_articolo,
                quantita,
                data_spedizione,
                priorita_cliente,
                note
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ARTICLE,
                "SYNTH-CODE-001",
                12,
                "2026-08-04",
                "ALTA",
                "synthetic test record",
            ),
        )
        self.anchor.commit()

    def connect_readonly(self):
        connection = sqlite3.connect(self.uri, uri=True)
        connection.execute("PRAGMA query_only = ON")
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        connection.set_trace_callback(self.statements.append)
        return connection

    def snapshot(self) -> list[tuple]:
        return self.anchor.execute(
            """
            SELECT articolo, codice_articolo, quantita, data_spedizione,
                   priorita_cliente, note
            FROM customer_demand
            ORDER BY id
            """
        ).fetchall()

    def close(self) -> None:
        self.anchor.close()


@pytest.fixture
def customer_demand_database():
    database = InMemoryCustomerDemandDatabase()
    try:
        yield database
    finally:
        database.close()


def _configure_customer_demand_path(monkeypatch, database):
    authorization = authorize_customer_demand_runtime()
    assert authorization.authorized is True

    def reader(**kwargs):
        return read_customer_demand(
            **kwargs,
            connection_factory=database.connect_readonly,
        )

    def resolve_with_test_database(**kwargs):
        return resolve_customer_demand_context(
            **kwargs,
            reader=reader,
            authorizer=authorize_customer_demand_runtime,
        )

    monkeypatch.setattr(
        tl_chat_api,
        "resolve_customer_demand_context",
        resolve_with_test_database,
    )
    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)
    monkeypatch.setattr(
        tl_chat_api,
        "build_governed_retrieval_pack",
        lambda question, article, limit: {
            "mode": "GOVERNED_RETRIEVAL_001",
            "question": question,
            "article": article,
            "evidence": [],
            "constraints": ["read-only"],
            "allowed_sources": ["customer_demand_registry"],
            "blocked_sources": [],
        },
    )


def _ask_customer_requested_date(article: str):
    return TestClient(app).post(
        "/tl/chat",
        json={
            "question": "Qual è la data richiesta dal cliente?",
            "context": {"article": article},
        },
    )


def test_tl_chat_reads_customer_demand_end_to_end_without_mutation(
    monkeypatch,
    customer_demand_database,
):
    before = customer_demand_database.snapshot()
    _configure_customer_demand_path(monkeypatch, customer_demand_database)

    response = _ask_customer_requested_date(ARTICLE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "customer_demand_registry"
    assert payload["source_status"] == "SOURCE_FOUND"
    assert payload["semantic_status"] == "DA_VERIFICARE"
    assert payload["confidence"] == "DA_VERIFICARE"
    assert payload["requires_confirmation"] is True
    assert "SYNTH-CODE-001" in payload["answer"]
    assert "Quantità richiesta: 12" in payload["answer"]
    assert "Data richiesta dal cliente registrata nella fonte: 2026-08-04" in payload["answer"]
    assert "non è una data confermata" in payload["answer"]
    assert payload.get("missing_data") is None
    assert customer_demand_database.statements
    assert all(
        statement.lstrip().upper().startswith("SELECT ")
        for statement in customer_demand_database.statements
    )
    assert customer_demand_database.snapshot() == before


def test_tl_chat_declares_missing_customer_demand_without_inventing_data(
    monkeypatch,
    customer_demand_database,
):
    before = customer_demand_database.snapshot()
    _configure_customer_demand_path(monkeypatch, customer_demand_database)

    response = _ask_customer_requested_date("SYNTH-MISSING")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "customer_demand_registry"
    assert payload["source_status"] == "SOURCE_FOUND"
    assert payload["semantic_status"] == "DA_VERIFICARE"
    assert payload["confidence"] == "DA_VERIFICARE"
    assert payload["missing_data"] == ["record_customer_demand_not_found"]
    assert "nessuna domanda cliente registrata" in payload["answer"]
    assert "2026-08-04" not in payload["answer"]
    assert customer_demand_database.statements
    assert all(
        statement.lstrip().upper().startswith("SELECT ")
        for statement in customer_demand_database.statements
    )
    assert customer_demand_database.snapshot() == before


def test_tl_chat_customer_demand_lookup_is_parameterized_and_cannot_mutate(
    monkeypatch,
    customer_demand_database,
):
    before = customer_demand_database.snapshot()
    _configure_customer_demand_path(monkeypatch, customer_demand_database)

    response = _ask_customer_requested_date(
        "SYNTH-CD-001'; DELETE FROM customer_demand; --"
    )

    assert response.status_code == 200
    assert response.json()["missing_data"] == ["record_customer_demand_not_found"]
    assert customer_demand_database.statements
    assert all(
        statement.lstrip().upper().startswith("SELECT ")
        for statement in customer_demand_database.statements
    )
    assert customer_demand_database.snapshot() == before


def test_tl_chat_planning_request_does_not_use_customer_demand_reader(monkeypatch):
    calls: list[dict] = []

    def fail_if_called(**kwargs):
        calls.append(kwargs)
        raise AssertionError("planning request must not query customer demand")

    monkeypatch.setattr(
        tl_chat_api,
        "resolve_customer_demand_context",
        fail_if_called,
    )
    monkeypatch.setattr(tl_chat_api, "_load_lifecycle_registry", lambda: {})
    monkeypatch.setattr(tl_chat_api, "_load_local_specs_metadata", lambda _article: None)

    response = TestClient(app).post(
        "/tl/chat",
        json={
            "question": "Pianifica il turno e conferma la spedizione.",
            "context": {"article": ARTICLE},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert calls == []
    assert payload.get("source") != "customer_demand_registry"
    assert "2026-08-04" not in payload["answer"]
