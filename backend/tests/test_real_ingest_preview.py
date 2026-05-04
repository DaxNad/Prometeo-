from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.api import real_ingest as real_ingest_api


class _FakeSMFReader:
    def __init__(self, *, found: bool = True, error: str | None = None) -> None:
        self.found = found
        self.error = error

    def code_exists(self, code: str) -> dict:
        payload = {
            "ok": self.error is None,
            "found": self.found,
            "sheet": "Codici",
            "column": "Codice",
            "matched_column": "Codice" if self.found else None,
            "code": code,
        }
        if self.error:
            payload["error"] = self.error
        return payload


def _client_with_code_registry(*, found: bool = True, error: str | None = None) -> TestClient:
    app.dependency_overrides[real_ingest_api._get_smf_reader] = lambda: _FakeSMFReader(
        found=found,
        error=error,
    )
    return TestClient(app)


def test_real_ingest_order_preview_requires_route():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-001",
            "codice": "12056",
            "qta": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert "route" in data["error"]


def test_real_ingest_order_preview_builds_smfrow_without_write():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-002",
            "cliente": "TEST",
            "codice": "12056",
            "qta": 10,
            "due_date": "2026-05-10",
            "priority": "ALTA",
            "postazione": "ZAW-1",
            "route": ["ZAW-1", "CP"],
            "note": "preview densificazione dominio reale",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["validated"] is True
    assert data["validation"]["is_valid"] is True
    assert data["validation"]["missing_fields"] == []
    assert data["validation"]["warnings"] == []
    assert data["validation"]["blocking_errors"] == []
    assert data["code_validation"]["status"] == "CERTO"
    assert data["code_validation"]["found"] is True
    assert data["code_validation"]["code"] == "12056"

    preview = data["smf_row_preview"]
    assert preview["id"] == "REAL-PREVIEW-TEST-002"
    assert preview["codice_articolo"] == "12056"
    assert preview["quantita"] == 10
    assert preview["cliente"] == "TEST"
    assert preview["data_scadenza"] == "2026-05-10"
    assert preview["priorita"] == "ALTA"
    assert preview["postazione_principale"] == "ZAW-1"
    assert preview["route"] == ["ZAW-1", "CP"]
    assert preview["stato"] == "DA_VALIDARE"
    assert preview["origine"] == "REAL_INGEST_PREVIEW"

    assert "nessuna scrittura" in data["note"]


def test_real_ingest_order_preview_warns_without_final_cp():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-003",
            "codice": "12056",
            "qta": 10,
            "route": ["ZAW-1"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["validation"]["is_valid"] is True
    assert "route_without_final_CP" in data["validation"]["warnings"]

def test_real_ingest_order_preview_normalizes_station_aliases():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-004",
            "codice": "12056",
            "qta": 10,
            "postazione": "ZAW1",
            "route": ["ZAW1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["smf_row_preview"]["postazione_principale"] == "ZAW-1"
    assert data["smf_row_preview"]["route"] == ["ZAW-1", "CP"]
    assert data["validation"]["blocking_errors"] == []


def test_real_ingest_order_preview_blocks_unknown_route_station():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-005",
            "codice": "12056",
            "qta": 10,
            "route": ["BANCO-FANTASMA", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert data["validation"]["is_valid"] is False
    assert any(
        item.startswith("unknown_route_stations")
        for item in data["validation"]["blocking_errors"]
    )


def test_real_ingest_order_preview_warns_on_postazione_route_mismatch():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-006",
            "codice": "12056",
            "qta": 10,
            "postazione": "ZAW-2",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert "postazione_mismatch_route_start" in data["validation"]["warnings"]

def test_real_ingest_order_preview_marks_unknown_code_as_da_verificare():
    client = _client_with_code_registry(found=False)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-007",
            "codice": "ART-NUOVO",
            "qta": 10,
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["code_validation"]["status"] == "DA_VERIFICARE"
    assert data["code_validation"]["found"] is False
    assert "codice_da_verificare" in data["validation"]["warnings"]


def test_real_ingest_order_preview_marks_code_registry_error_as_da_verificare():
    client = _client_with_code_registry(found=False, error="sheet Codici not found")

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-008",
            "codice": "12056",
            "qta": 10,
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["code_validation"]["status"] == "DA_VERIFICARE"
    assert data["code_validation"]["error"] == "sheet Codici not found"
    assert "codice_registry_non_accessibile" in data["validation"]["warnings"]

def test_real_ingest_order_preview_does_not_bootstrap_missing_smf_dir(monkeypatch, tmp_path):
    base = tmp_path / "missing_smf_dir"
    monkeypatch.setenv("SMF_BASE_PATH", str(base))
    app.dependency_overrides.pop(real_ingest_api._get_smf_reader, None)

    client = TestClient(app)

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-009",
            "codice": "12056",
            "qta": 10,
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["code_validation"]["status"] == "DA_VERIFICARE"
    assert data["code_validation"]["error"] == "file not found"
    assert "codice_registry_non_accessibile" in data["validation"]["warnings"]
    assert not base.exists()

def test_real_ingest_order_preview_blocks_non_positive_quantity():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-010",
            "codice": "12056",
            "qta": 0,
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert data["validation"]["is_valid"] is False
    assert "qta_not_positive" in data["validation"]["blocking_errors"]


def test_real_ingest_order_preview_blocks_non_numeric_quantity():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-011",
            "codice": "12056",
            "qta": "abc",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is False
    assert data["validation"]["is_valid"] is False
    assert "qta_not_numeric" in data["validation"]["blocking_errors"]


def test_real_ingest_order_preview_warns_on_non_iso_due_date():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-012",
            "codice": "12056",
            "qta": 10,
            "due_date": "10/05/2026",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert "due_date_not_iso" in data["validation"]["warnings"]


def test_real_ingest_order_preview_warns_on_unknown_priority():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-013",
            "codice": "12056",
            "qta": 10,
            "priority": "URGENTISSIMA",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["smf_row_preview"]["priorita"] == "MEDIA"
    assert "priority_unknown" in data["validation"]["warnings"]


def test_real_ingest_order_preview_normalizes_decimal_quantity_string():
    client = _client_with_code_registry()

    response = client.post(
        "/real/ingest-order",
        json={
            "order_id": "REAL-PREVIEW-TEST-014",
            "codice": "12056",
            "qta": "12,5",
            "due_date": "2026-05-10",
            "priority": "alta",
            "route": ["ZAW-1", "CP"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["smf_row_preview"]["quantita"] == 12.5
    assert data["smf_row_preview"]["data_scadenza"] == "2026-05-10"
    assert data["smf_row_preview"]["priorita"] == "ALTA"
    assert "priority_unknown" not in data["validation"]["warnings"]

