"""
migrate_to_db.py — One-time migration of existing OPENBRAIN data into SQLite.
Reads all *_DB.jsonl, *_ToDo.csv, and receipts.jsonl files across the 5C domains.
Safe to run multiple times — skips records that already exist by checking content hash.
"""
import json
import csv
import uuid
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import db

OPENBRAIN_ROOT = Path("/home/workspace/OPENBRAIN")

CANONICAL_DOMAINS = {
    "CAPITAL": "CAPITAL",
    "COMPUTERS": "COMPUTERS",
    "CARS": "CARS",
    "CANNAPY": "CANNAPY",
    "CLAN": "CLAN",
}

# Short-form folder aliases → skip (data is in canonical folder)
SKIP_FOLDERS = {"COMP", "CAP", "CANN"}


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def already_exists(conn, content: str, domain: str) -> bool:
    tag = content_hash(content)
    row = conn.execute(
        "SELECT id FROM items WHERE domain=? AND metadata LIKE ?",
        (domain, f'%"migration_hash": "{tag}"%')
    ).fetchone()
    return row is not None


def migrate_jsonl(conn, filepath: Path, domain: str, category: str):
    """Migrate a *_DB.jsonl file."""
    count = 0
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            content = entry.get('summary') or entry.get('content') or entry.get('title') or str(entry)
            if already_exists(conn, content, domain):
                continue

            meta = {k: v for k, v in entry.items()
                    if k not in ('domain', 'category', 'title', 'summary', 'tags', 'created_at')}
            meta['migration_hash'] = content_hash(content)
            meta['migrated_from'] = str(filepath)

            conn.execute("""
                INSERT INTO items (id, domain, category, item_type, title, content, source, tags, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                domain,
                entry.get('category', category),
                entry.get('intent', 'note'),
                entry.get('title', ''),
                content,
                'migration',
                json.dumps(entry.get('tags', [])),
                json.dumps(meta),
                entry.get('created_at', datetime.now(timezone.utc).isoformat()),
                datetime.now(timezone.utc).isoformat()
            ))
            count += 1
    return count


def migrate_csv_todos(conn, filepath: Path, domain: str):
    """Migrate a *_ToDo.csv file into items as Tasks."""
    count = 0
    try:
        with open(filepath, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc = row.get('task_description') or row.get('description') or str(row)
                if not desc.strip():
                    continue
                if already_exists(conn, desc, domain):
                    continue

                meta = dict(row)
                meta['migration_hash'] = content_hash(desc)
                meta['migrated_from'] = str(filepath)

                conn.execute("""
                    INSERT INTO items (id, domain, category, item_type, title, content, status, priority, source, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    domain,
                    'Tasks',
                    'task',
                    desc[:80],
                    desc,
                    row.get('status', 'active'),
                    int(row.get('priority', 0)) if str(row.get('priority', '')).isdigit() else 0,
                    'migration',
                    json.dumps(meta),
                    row.get('created_at', datetime.now(timezone.utc).isoformat()),
                    datetime.now(timezone.utc).isoformat()
                ))
                count += 1
    except Exception as e:
        print(f"  Warning: could not parse {filepath}: {e}")
    return count


def migrate_receipts(conn, filepath: Path, domain: str):
    """Migrate inbox_log receipts.jsonl into inbox_log table (historical)."""
    count = 0
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            raw = entry.get('source_raw') or entry.get('raw_content') or str(entry)
            row_id = str(uuid.uuid4())
            try:
                conn.execute("""
                    INSERT INTO inbox_log
                        (id, raw_content, source, classified_domain, classified_category,
                         classified_title, classified_summary, classified_tags, quality_score,
                         bouncer_decision, processed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row_id,
                    raw,
                    'migration',
                    entry.get('domain', domain),
                    entry.get('category', 'Inbox Log'),
                    entry.get('title', ''),
                    entry.get('summary', ''),
                    json.dumps(entry.get('tags', [])),
                    entry.get('quality_score', 'medium'),
                    'pass',
                    1,
                    entry.get('created_at', datetime.now(timezone.utc).isoformat())
                ))
                count += 1
            except sqlite3.IntegrityError:
                pass
    return count


def run():
    db.init_db()
    print(f"DB: {db.DB_PATH}")

    conn = sqlite3.connect(db.DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    total = 0

    for folder in sorted(OPENBRAIN_ROOT.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name in SKIP_FOLDERS:
            print(f"Skipping alias folder: {folder.name}")
            continue
        domain = CANONICAL_DOMAINS.get(folder.name.upper())
        if not domain:
            continue

        print(f"\n── {domain} ──────────────────")

        # Main DB jsonl files
        for jsonl in folder.rglob('*_DB.jsonl'):
            cat = jsonl.parent.name if jsonl.parent != folder else 'Inbox Log'
            n = migrate_jsonl(conn, jsonl, domain, cat)
            print(f"  {jsonl.relative_to(OPENBRAIN_ROOT)}: {n} items")
            total += n

        # ToDo CSVs
        for csv_file in folder.rglob('*_ToDo.csv'):
            n = migrate_csv_todos(conn, csv_file, domain)
            print(f"  {csv_file.relative_to(OPENBRAIN_ROOT)}: {n} tasks")
            total += n

        # Receipts
        for receipt in folder.rglob('receipts.jsonl'):
            n = migrate_receipts(conn, receipt, domain)
            print(f"  {receipt.relative_to(OPENBRAIN_ROOT)}: {n} inbox entries")
            total += n

    conn.commit()
    conn.close()
    print(f"\nMigration complete — {total} records written to {db.DB_PATH}")


if __name__ == "__main__":
    run()
