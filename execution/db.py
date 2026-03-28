"""
db.py — OpenBrain SQLite data access layer
All reads/writes to openbrain.db go through this module.
No script should write directly to the DB file.
"""
import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Load .env before reading DB_PATH so container env is populated
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

DB_PATH = Path(os.getenv("OPENBRAIN_DB_PATH", "/home/workspace/OPENBRAIN/openbrain.db"))

VALID_DOMAINS = {"CAPITAL", "COMPUTERS", "CARS", "CANNAPY", "CLAN"}
VALID_CATEGORIES = {"People", "Projects", "Ideas", "Admin", "Tasks", "Thoughts", "Inbox Log"}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and indexes if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id          TEXT PRIMARY KEY,
                domain      TEXT NOT NULL,
                category    TEXT NOT NULL,
                item_type   TEXT DEFAULT 'note',
                title       TEXT,
                content     TEXT,
                status      TEXT DEFAULT 'active',
                priority    INTEGER DEFAULT 0,
                source      TEXT DEFAULT 'telegram',
                agent       TEXT,
                tags        TEXT,
                metadata    TEXT,
                created_at  TEXT DEFAULT (datetime('now')),
                updated_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS inbox_log (
                id                   TEXT PRIMARY KEY,
                raw_content          TEXT NOT NULL,
                source               TEXT DEFAULT 'telegram',
                sender_id            TEXT,
                classified_domain    TEXT,
                classified_category  TEXT,
                classified_item_type TEXT,
                classified_title     TEXT,
                classified_summary   TEXT,
                classified_tags      TEXT,
                classified_metadata  TEXT,
                quality_score        TEXT,
                bouncer_decision     TEXT DEFAULT 'pending',
                bouncer_reason       TEXT,
                processed            INTEGER DEFAULT 0,
                item_id              TEXT REFERENCES items(id),
                created_at           TEXT DEFAULT (datetime('now')),
                processed_at         TEXT
            );

            CREATE TABLE IF NOT EXISTS digests (
                id             TEXT PRIMARY KEY,
                domain         TEXT,
                digest_type    TEXT DEFAULT 'daily',
                content        TEXT,
                items_included TEXT,
                sent_at        TEXT,
                created_at     TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_items_domain    ON items(domain);
            CREATE INDEX IF NOT EXISTS idx_items_category  ON items(category);
            CREATE INDEX IF NOT EXISTS idx_items_status    ON items(status);
            CREATE INDEX IF NOT EXISTS idx_inbox_processed ON inbox_log(processed);
            CREATE INDEX IF NOT EXISTS idx_inbox_domain    ON inbox_log(classified_domain);
        """)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def add_to_inbox(raw_content: str, source: str = "telegram", sender_id: str = None) -> str:
    """Insert a raw message into inbox_log. Returns the new row ID."""
    row_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO inbox_log (id, raw_content, source, sender_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (row_id, raw_content, source, str(sender_id) if sender_id else None, _now())
        )
    return row_id


def update_inbox_classification(inbox_id: str, classified: dict):
    """Update an inbox_log row with Sorter classification results."""
    with get_conn() as conn:
        conn.execute("""
            UPDATE inbox_log SET
                classified_domain    = ?,
                classified_category  = ?,
                classified_item_type = ?,
                classified_title     = ?,
                classified_summary   = ?,
                classified_tags      = ?,
                classified_metadata  = ?,
                quality_score        = ?
            WHERE id = ?
        """, (
            classified.get("domain"),
            classified.get("category"),
            classified.get("intent"),
            classified.get("title"),
            classified.get("summary"),
            json.dumps(classified.get("tags", [])),
            json.dumps(classified.get("metadata", {})),
            classified.get("quality_score"),
            inbox_id
        ))


def promote_to_items(inbox_id: str, classified: dict, source: str = "telegram") -> str:
    """Promote a classified inbox entry to items. Marks inbox row as processed."""
    item_id = str(uuid.uuid4())
    now = _now()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO items
                (id, domain, category, item_type, title, content, source, tags, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            classified.get("domain", "CLAN"),
            classified.get("category", "Inbox Log"),
            classified.get("intent", "note"),
            classified.get("title"),
            classified.get("summary") or classified.get("source_raw", ""),
            source,
            json.dumps(classified.get("tags", [])),
            json.dumps(classified.get("metadata", {})),
            now,
            now
        ))
        conn.execute("""
            UPDATE inbox_log
            SET processed = 1, bouncer_decision = 'pass', item_id = ?, processed_at = ?
            WHERE id = ?
        """, (item_id, now, inbox_id))
    return item_id


def flag_inbox(inbox_id: str, reason: str):
    """Mark an inbox entry as flagged by Bouncer — stays unprocessed for human review."""
    with get_conn() as conn:
        conn.execute("""
            UPDATE inbox_log SET bouncer_decision = 'flag', bouncer_reason = ?
            WHERE id = ?
        """, (reason, inbox_id))


def get_items(domain: str = None, category: str = None, status: str = "active", limit: int = 100) -> list:
    """Query items with optional domain/category filters."""
    query = "SELECT * FROM items WHERE status = ?"
    params = [status]
    if domain:
        query += " AND domain = ?"
        params.append(domain.upper())
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_unprocessed_inbox(limit: int = 50) -> list:
    """Return inbox_log rows pending human review (flagged or unclassified)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM inbox_log WHERE processed = 0 ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print(f"DB initialized at {DB_PATH}")
