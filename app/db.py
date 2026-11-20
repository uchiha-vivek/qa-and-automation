"""Tiny SQLite data layer."""
import sqlite3
from datetime import datetime

from app import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT NOT NULL,
    email           TEXT NOT NULL,
    subject         TEXT,
    message         TEXT NOT NULL,
    category        TEXT,
    priority        TEXT,
    sentiment       TEXT,
    confidence      REAL,
    language        TEXT,
    suggested_reply TEXT,
    ai_category     TEXT,
    ai_priority     TEXT,
    status          TEXT DEFAULT 'open',
    created_at      TEXT,
    updated_at      TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id   INTEGER,
    action      TEXT,
    old_value   TEXT,
    new_value   TEXT,
    agent_name  TEXT,
    created_at  TEXT
);
"""


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds") + "Z"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def insert_ticket(data: dict) -> int:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO tickets (customer_name, email, subject, message, category, priority,
                   sentiment, confidence, language, suggested_reply, ai_category, ai_priority,
                   status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                data["customer_name"], data["email"], data.get("subject", ""), data["message"],
                data["category"], data["priority"], data["sentiment"], data["confidence"],
                data["language"], data["suggested_reply"], data["category"], data["priority"],
                "open", ts, ts,
            ),
        )
        return cur.lastrowid


def get_ticket(ticket_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def list_tickets(priority=None, category=None, status=None, q=None) -> list:
    clauses, params = [], []
    if priority:
        clauses.append("priority >= ?")
        params.append(priority)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if q:
        clauses.append("instr(subject || ' ' || message, ?) > 0")
        params.append(q)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM tickets {where} ORDER BY id DESC", params).fetchall()
        return [dict(r) for r in rows]


def update_ticket(ticket_id: int, fields: dict) -> None:
    fields = {**fields, "updated_at": now_iso()}
    sets = ", ".join(f"{k} = ?" for k in fields)
    with get_conn() as conn:
        conn.execute(f"UPDATE tickets SET {sets} WHERE id = ?", (*fields.values(), ticket_id))


def add_audit(ticket_id: int, action: str, old_value: str, new_value: str, agent_name) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_log (ticket_id, action, old_value, new_value, agent_name, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (ticket_id, action, old_value, new_value, agent_name, now_iso()),
        )


def get_audit(ticket_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE ticket_id = ? ORDER BY id", (ticket_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def count(sql: str) -> int:
    with get_conn() as conn:
        return conn.execute(sql).fetchone()[0]
