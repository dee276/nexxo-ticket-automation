import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("tickets.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema = Path("schema.sql").read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(schema)

def insert_ticket(source: str, subject: str, body: str, category: str, priority: str, confidence: float, routed_to: str):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tickets (source, subject, body, category, priority, confidence, routed_to, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (source, subject, body, category, priority, confidence, routed_to, now),
        )
        return cur.lastrowid

def list_tickets(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, source, subject, category, priority, confidence, routed_to, created_at FROM tickets ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]