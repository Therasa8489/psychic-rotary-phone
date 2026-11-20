import sqlite3

DB_PATH = "nalla.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  clip_path TEXT NOT NULL,
  incident_type TEXT NOT NULL,      -- fine / accident / dispute / litter
  sha256 TEXT,
  created_at TEXT NOT NULL,
  retain_until TEXT NOT NULL,
  legal_hold INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  evidence_id TEXT,
  at TEXT NOT NULL
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as c:
        c.executescript(SCHEMA)
