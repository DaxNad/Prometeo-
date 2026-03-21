from .db import get_connection


def insert_event(code, station, event_type, operator=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO events (code, station, event_type, operator)
        VALUES (%s,%s,%s,%s)
        RETURNING *
        """,
        (code, station, event_type, operator)
    )

    event = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return event


def list_events():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM events
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
