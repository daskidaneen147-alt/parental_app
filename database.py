# ============================================================
#  backend/database.py  —  SQLite database layer
#  Handles: users table, children table, activity logs
# ============================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "guardian_eye.db")


def get_connection():
    """Open (or create) the SQLite database and return connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Rows act like dictionaries
    return conn


def initialize_db():
    """
    Create all tables if they don't exist yet.
    Call this once when the app starts.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── Parents / guardians table ──────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parents (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Children profiles table ────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS children (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id    INTEGER NOT NULL,
            name         TEXT    NOT NULL,
            age          INTEGER,
            device_id    TEXT,
            daily_limit  INTEGER DEFAULT 120,   -- minutes
            is_online    INTEGER DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES parents(id)
        )
    """)

    # ── Blocked apps table ─────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocked_apps (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id   INTEGER NOT NULL,
            app_name   TEXT    NOT NULL,
            package    TEXT,
            blocked_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (child_id) REFERENCES children(id)
        )
    """)

    # ── Screen time logs ───────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS screen_time_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id   INTEGER NOT NULL,
            date       TEXT    NOT NULL,
            minutes    INTEGER DEFAULT 0,
            FOREIGN KEY (child_id) REFERENCES children(id)
        )
    """)

    # ── Location history ───────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id   INTEGER NOT NULL,
            latitude   REAL,
            longitude  REAL,
            address    TEXT,
            logged_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (child_id) REFERENCES children(id)
        )
    """)

    # ── Notifications / alerts table ───────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id   INTEGER NOT NULL,
            parent_id  INTEGER NOT NULL,
            message    TEXT    NOT NULL,
            alert_type TEXT    DEFAULT 'info',   -- info | warning | danger
            is_read    INTEGER DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (child_id)  REFERENCES children(id),
            FOREIGN KEY (parent_id) REFERENCES parents(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


# ── CRUD helpers ───────────────────────────────────────────

def fetch_all(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_one(query, params=()):
    conn = get_connection()
    row  = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None


def execute_query(query, params=()):
    conn = get_connection()
    cur  = conn.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id