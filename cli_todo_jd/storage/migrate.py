from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .schema import ensure_schema


def _iter_json_items(data: object) -> Iterable[str]:
    """Yield todo item strings from supported legacy JSON formats.

    Supported:
    - ["item1", "item2", ...]
    - [{"item": "..."}, {"text": "..."}, ...]
    """
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, str):
                text = entry
            elif isinstance(entry, dict):
                text = entry.get("item") or entry.get("text")
                if not isinstance(text, str):
                    continue
            else:
                continue

            text = text.strip()
            if text:
                yield text


def migrate_from_json(
    *,
    json_path: Path,
    db_path: Path,
    backup: bool = True,
) -> int:
    """Migrate todos from a legacy JSON file into a SQLite database.

    Parameters
    ----------
    json_path:
        Path to legacy JSON file (e.g. `.todo_list.json`).
    db_path:
        Path to SQLite file (e.g. `.todo_list.db`).
    backup:
        If True, rename the JSON file to `.bak` after successful import.

    Returns
    -------
    int
        Number of rows inserted.

    Behavior
    --------
    - If the JSON file doesn't exist, returns 0.
    - If the database already has todos, does not import (returns 0).
      (This avoids duplicate imports when multiple commands run.)
    """

    if not json_path.exists():
        return 0

    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        raw = json_path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else []
    except (OSError, json.JSONDecodeError):
        # Fail safe: don't destroy/rename the user's file.
        return 0

    items = list(_iter_json_items(data))
    if not items:
        return 0

    inserted = 0
    with sqlite3.connect(db_path) as conn:
        ensure_schema(conn)

        # Guard against double-import
        existing = conn.execute("SELECT 1 FROM todos LIMIT 1;").fetchone()
        if existing is not None:
            return 0

        with conn:
            conn.executemany(
                "INSERT INTO todos(item, done) VALUES (?, 0);", [(t,) for t in items]
            )
            inserted = conn.execute("SELECT changes();").fetchone()[0]

    if backup:
        try:
            bak_path = json_path.with_suffix(json_path.suffix + ".bak")
            if bak_path.exists():
                # Avoid overwrite; add a numeric suffix
                i = 1
                while True:
                    candidate = json_path.with_suffix(json_path.suffix + f".bak{i}")
                    if not candidate.exists():
                        bak_path = candidate
                        break
                    i += 1
            json_path.rename(bak_path)
        except OSError:
            # Backup failure shouldn't invalidate a successful migration
            pass

    return inserted
