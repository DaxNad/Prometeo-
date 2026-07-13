from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

from app.db import get_connection

SOURCE_ID = "customer_demand_registry"
ALLOWED_FIELDS = (
    "articolo",
    "codice_articolo",
    "quantita",
    "data_spedizione",
    "priorita_cliente",
)

_QUERIES = {
    "articolo": (
        "SELECT articolo, codice_articolo, quantita, data_spedizione, priorita_cliente "
        "FROM customer_demand WHERE articolo = %s "
        "ORDER BY data_spedizione NULLS LAST, codice_articolo NULLS LAST LIMIT %s"
    ),
    "codice_articolo": (
        "SELECT articolo, codice_articolo, quantita, data_spedizione, priorita_cliente "
        "FROM customer_demand WHERE codice_articolo = %s "
        "ORDER BY data_spedizione NULLS LAST, articolo NULLS LAST LIMIT %s"
    ),
}


class CustomerDemandReaderInputError(ValueError):
    pass


def read_customer_demand(
    *,
    articolo: str | None = None,
    codice_articolo: str | None = None,
    limit: int = 50,
    connection_factory: Callable[[], Any] = get_connection,
) -> dict[str, Any]:
    field, value = _validate(articolo, codice_articolo, limit)
    connection = connection_factory()
    cursor = None
    try:
        set_session = getattr(connection, "set_session", None)
        if callable(set_session):
            set_session(readonly=True, autocommit=False)
        cursor = connection.cursor()
        statement = _statement_for_connection(connection, _QUERIES[field])
        cursor.execute(statement, (value, limit))
        records = [_normalize(row) for row in cursor.fetchall()]
    finally:
        if cursor is not None and callable(getattr(cursor, "close", None)):
            cursor.close()
        if callable(getattr(connection, "rollback", None)):
            connection.rollback()
        if callable(getattr(connection, "close", None)):
            connection.close()

    return {
        "source_id": SOURCE_ID,
        "source_status": "SOURCE_FOUND",
        "runtime_binding": "UNBOUND",
        "lookup": {"field": field, "value": value, "limit": limit},
        "records": records,
        "freshness": "UNKNOWN",
        "semantic_status": "DA_VERIFICARE",
        "confidence": "LOW_UNTIL_FRESHNESS_VERIFIED",
        "missing_data": [] if records else ["record_customer_demand_not_found"],
    }


def _statement_for_connection(connection: Any, statement: str) -> str:
    module_name = connection.__class__.__module__.lower()
    if module_name.startswith("sqlite3"):
        return statement.replace("%s", "?")
    return statement


def _validate(
    articolo: str | None,
    codice_articolo: str | None,
    limit: int,
) -> tuple[str, str]:
    provided = [("articolo", articolo), ("codice_articolo", codice_articolo)]
    provided = [(field, value) for field, value in provided if value is not None]
    if len(provided) != 1:
        raise CustomerDemandReaderInputError("provide exactly one lookup field")
    field, value = provided[0]
    if not isinstance(value, str) or not value.strip():
        raise CustomerDemandReaderInputError("lookup value must be a non-empty string")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise CustomerDemandReaderInputError("limit must be between 1 and 100")
    return field, value.strip()


def _normalize(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        values = {field: row.get(field) for field in ALLOWED_FIELDS}
    elif isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)):
        if len(row) != len(ALLOWED_FIELDS):
            raise RuntimeError("unexpected customer_demand row shape")
        values = dict(zip(ALLOWED_FIELDS, row, strict=True))
    else:
        raise RuntimeError("unsupported customer_demand row type")
    return {key: _json_safe(value) for key, value in values.items()}


def _json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
