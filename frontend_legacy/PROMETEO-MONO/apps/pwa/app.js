from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import json

app = FastAPI()

DB_PATH = "orders.db"


# ---------- DATABASE ----------

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ORDERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            descrizione TEXT,
            stato TEXT,
            priorita INTEGER,
            componenti TEXT,
            note TEXT,
            turno TEXT,
            updated_at TEXT
        )
    """)

    # HISTORY TABLE (strutturata)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            old_state TEXT,
            new_state TEXT,
            timestamp TEXT,
            payload TEXT
        )
    """)

    # SEED DATA
    cur.execute("SELECT COUNT(*) FROM orders")

    if cur.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat()

        cur.executemany("""
            INSERT INTO orders
            (id, descrizione, stato, priorita, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (12054, "manca tubo X — cluster HENN", "critico", 1, now),
            (50027, "parziale connettori", "attenzione", 2, now),
            (468845, "pronto", "ok", 3, now),
        ])

    conn.commit()
    conn.close()


init_db()


# ---------- MODELS ----------

class OrderUpdate(BaseModel):
    descrizione: str
    stato: str
    priorita: int
    componenti: str | None = ""
    note: str | None = ""
    turno: str | None = ""


# ---------- API ----------

@app.get("/")
def root():
    return {"status": "PROMETEO API online"}


@app.get("/api/orders")
def get_orders():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()

    conn.close()

    return [dict(row) for row in rows]


@app.post("/api/orders/{order_id}")
def update_order(order_id: int, data: OrderUpdate):
    conn = get_conn()
    cur = conn.cursor()

    # stato precedente
    cur.execute("SELECT stato FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return {"error": "order not found"}

    old_state = row["stato"]
    now = datetime.utcnow().isoformat()

    # update ordine
    cur.execute("""
        UPDATE orders
        SET descrizione = ?,
            stato = ?,
            priorita = ?,
            componenti = ?,
            note = ?,
            turno = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        data.descrizione,
        data.stato,
        data.priorita,
        data.componenti,
        data.note,
        data.turno,
        now,
        order_id
    ))

    # storico strutturato
    cur.execute("""
        INSERT INTO history
        (order_id, old_state, new_state, timestamp, payload)
        VALUES (?, ?, ?, ?, ?)
    """, (
        order_id,
        old_state,
        data.stato,
        now,
        json.dumps(data.dict())
    ))

    conn.commit()
    conn.close()

    return {"status": "updated", "id": order_id, "updated_at": now}


@app.get("/api/history/{order_id}")
def get_history(order_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM history
        WHERE order_id = ?
        ORDER BY timestamp DESC
    """, (order_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]
