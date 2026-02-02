from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from cli_todo_jd.storage.schema import ensure_schema
from cli_todo_jd.storage.migrate import migrate_from_json


def create_app(db_path: Path) -> Flask:
    app = Flask(__name__)
    app.config["TODO_DB_PATH"] = str(db_path)

    def _connect() -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        ensure_schema(conn)
        return conn

    # Optional one-time JSON migration (mirrors CLI behavior)
    json_path = db_path.with_suffix(".json")
    if json_path.exists() and db_path.suffix == ".db":
        migrate_from_json(json_path=json_path, db_path=db_path, backup=True)

    @app.get("/")
    def index():
        show = request.args.get("show", "open")
        if show not in {"open", "done", "all"}:
            show = "open"

        with _connect() as conn:
            if show == "open":
                todos = conn.execute(
                    "SELECT id, item, done, created_at, done_at FROM todos WHERE done = ? ORDER BY id DESC",
                    (0,),
                ).fetchall()
            elif show == "done":
                todos = conn.execute(
                    "SELECT id, item, done, created_at, done_at FROM todos WHERE done = ? ORDER BY id DESC",
                    (1,),
                ).fetchall()
            else:
                todos = conn.execute(
                    "SELECT id, item, done, created_at, done_at FROM todos ORDER BY id DESC"
                ).fetchall()

        return render_template("index.html", todos=todos, show=show)

    @app.post("/add")
    def add():
        item = (request.form.get("item") or "").strip()
        if item:
            with _connect() as conn:
                with conn:
                    conn.execute("INSERT INTO todos(item, done) VALUES (?, 0)", (item,))
        return redirect(url_for("index"))

    @app.post("/toggle/<int:todo_id>")
    def toggle(todo_id: int):
        with _connect() as conn:
            row = conn.execute(
                "SELECT done FROM todos WHERE id = ?", (todo_id,)
            ).fetchone()
            if row is not None:
                new_done = 0 if row["done"] else 1
                with conn:
                    if new_done:
                        conn.execute(
                            "UPDATE todos SET done = 1, done_at = datetime('now') WHERE id = ?",
                            (todo_id,),
                        )
                    else:
                        conn.execute(
                            "UPDATE todos SET done = 0, done_at = NULL WHERE id = ?",
                            (todo_id,),
                        )
        return redirect(url_for("index"))

    @app.post("/delete/<int:todo_id>")
    def delete(todo_id: int):
        with _connect() as conn:
            with conn:
                conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        return redirect(url_for("index"))

    @app.post("/clear")
    def clear():
        if request.form.get("confirm") == "yes":
            with _connect() as conn:
                with conn:
                    conn.execute("DELETE FROM todos")
        return redirect(url_for("index"))

    return app


def run_web(
    db_path: Path, host: str = "127.0.0.1", port: int = 8000, debug: bool = False
) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    app = create_app(db_path)
    app.run(host=host, port=port, debug=debug)
