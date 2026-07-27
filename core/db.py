"""SQLite connection + schema bootstrap for the pipeline."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "biznis.sqlite3"
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Columns added to tables after their initial release. CREATE TABLE IF NOT
# EXISTS (in schema.sql) only helps on a fresh database - existing databases
# need an explicit ALTER TABLE to pick up new columns.
MIGRATIONS = [
    ("pages", "seo_enhanced", "INTEGER NOT NULL DEFAULT 0"),
    ("products", "monetization_url", "TEXT"),
    # 'core' = validated paid-demand evidence found (see docs/ROADMAP.md);
    # 'lead_magnet' = good content, no evidence people pay for it directly -
    # kept free on purpose; 'retire_candidate' = generic/saturated pattern,
    # not worth building more like it. NULL = not yet classified.
    ("products", "tier", "TEXT"),
]


def init_db() -> None:
    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    for table, column, coltype in MIGRATIONS:
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized database at {DB_PATH}")
