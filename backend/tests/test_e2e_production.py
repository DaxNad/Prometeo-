import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    r = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    assert r.status_code == 200
    data = r.json()

    assert isinstance(data, dict)

    if "status" in data:
        assert data["status"] == "ok"
    else:
        assert data.get("ok") is True


def test_create_order_and_board_visibility():
    order_id = f"E2E-{uuid.uuid4().hex[:8]}"

    payload = {
        "order_id": order_id,
        "cliente": "ClienteE2E",
        "codice": "CODE-E2E",
        "qta": 7,
        "postazione": "LINEA1",
        "stato": "da fare",
    }

    r = httpx.post(
        f"{BASE_URL}/production/order",
        json=payload,
        timeout=10.0,
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True

    r2 = httpx.get(f"{BASE_URL}/production/board", timeout=10.0)
    assert r2.status_code == 200
    board = r2.json()
    assert board.get("ok") is True

    items = board.get("items", [])
    found = [x for x in items if x.get("order_id") == order_id]
    assert found, f"ordine {order_id} non trovato in board"


def test_events_endpoint_available():
    r = httpx.get(f"{BASE_URL}/production/events", timeout=10.0)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "items" in data
