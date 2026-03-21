from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            descrizione TEXT,
            stato TEXT,
            priorita INTEGER,
            componenti TEXT,
            note TEXT,
            turno TEXT,
            version INTEGER DEFAULT 1,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            field TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp TEXT
        )
    """)

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
    version: int


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

    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Order not found")

    db_version = row["version"]

    if data.version != db_version:
        raise HTTPException(
            status_code=409,
            detail="Conflict: order modified by another user"
        )

    fields = [
        "descrizione",
        "stato",
        "priorita",
        "componenti",
        "note",
        "turno"
    ]

    now = datetime.utcnow().isoformat()

    for f in fields:
        old = row[f]
        new = getattr(data, f)

        if str(old) != str(new):
            cur.execute("""
                INSERT INTO order_history
                (order_id, field, old_value, new_value, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, f, str(old), str(new), now))

    new_version = db_version + 1

    cur.execute("""
        UPDATE orders
        SET descrizione=?,
            stato=?,
            priorita=?,
            componenti=?,
            note=?,
            turno=?,
            version=?,
            updated_at=?
        WHERE id=?
    """, (
        data.descrizione,
        data.stato,
        data.priorita,
        data.componenti,
        data.note,
        data.turno,
        new_version,
        now,
        order_id
    ))

    conn.commit()
    conn.close()

    return {
        "status": "updated",
        "id": order_id,
        "version": new_version
    }


@app.get("/api/history/{order_id}")
def get_history(order_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM order_history
        WHERE order_id=?
        ORDER BY timestamp DESC
    """, (order_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]
