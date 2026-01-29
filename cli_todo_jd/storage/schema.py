from __future__ import annotations

import sqlite3


SCHEMA_VERSION = 1


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure required SQLite schema exists and is migrated.

    Uses `PRAGMA user_version` for lightweight, in-app migrations.

    Parameters
    ----------
    conn:
        An open sqlite3 connection.

    Notes
    -----
    - Call this once per process/command, right after connecting.
    - Keep migrations idempotent and wrapped in a transaction.
    """

    # Improve concurrent CLI usage (separate processes) and durability.
    # WAL is persistent for the database file once set.
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")

    current_version = conn.execute("PRAGMA user_version;").fetchone()[0]

    # Fresh database
    if current_version == 0:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                  id         INTEGER PRIMARY KEY AUTOINCREMENT,
                  item       TEXT    NOT NULL,
                  done       INTEGER NOT NULL DEFAULT 0,
                  created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                  done_at    TEXT
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todos_done ON todos(done);")
            conn.execute(f"PRAGMA user_version = {int(SCHEMA_VERSION)};")
        return

    # Incremental migrations
    if current_version < 1:
        # Example placeholder for future migrations.
        # Keep each migration block small and bump user_version accordingly.
        with conn:
            conn.execute("PRAGMA user_version = 1;")
        current_version = 1

    # If you bump SCHEMA_VERSION, add `if current_version < N:` blocks above.
