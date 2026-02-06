from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.padding import Padding
import sqlite3
from cli_todo_jd.storage.schema import ensure_schema
from cli_todo_jd.storage.migrate import migrate_from_json


def main():
    TodoApp()


class TodoApp:
    """A simple command-line todo application."""

    def __init__(self, file_path_to_db="./.todo_list.db"):
        self.todo_ids: list[int] = []
        self.todos: list[str] = []
        self.status: list[int] = []
        self.file_path_to_db = Path(file_path_to_db)
        self._check_and_load_todos(self.file_path_to_db)
        self._console = Console()

    def reload_todos(self) -> None:
        self._check_and_load_todos(self.file_path_to_db)

    def add_todo(self, item: str) -> None:
        item = (item or "").strip()
        if not item:
            print("Error: Todo item cannot be empty.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                with conn:
                    conn.execute(
                        "INSERT INTO todos(item, done) VALUES (?, 0);", (item,)
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to add todo. ({e})")
            return

        print(f'Added todo: "{item}"')

    def list_todos(self, *, show: str = "open") -> None:
        """List todos.

        Parameters
        ----------
        show:
            "open" (default), "done", or "all".
        """
        show = (show or "open").lower()
        if show not in {"open", "done", "all"}:
            print("Error: show must be one of: open, done, all")
            return

        # Always read fresh so output reflects the DB
        self._check_and_load_todos(self.file_path_to_db)
        if not self.todos:
            print("Your todo list is empty! Start adding some with 'todo add <task>'")
            return

        if show == "all":
            self._table_print(title="Todos")
            return

        # Filter in-memory to keep this change minimal.
        filtered_ids: list[int] = []
        filtered_todos: list[str] = []
        filtered_status: list[int] = []
        for todo_id, todo, done in zip(
            self.todo_ids, self.todos, self.status, strict=False
        ):
            if show == "open" and not done:
                filtered_ids.append(todo_id)
                filtered_todos.append(todo)
                filtered_status.append(done)
            elif show == "done" and done:
                filtered_ids.append(todo_id)
                filtered_todos.append(todo)
                filtered_status.append(done)

        if not filtered_todos:
            print(f"No todos found when filtering on {show}.")
            return

        original_ids, original_todos, original_status = (
            self.todo_ids,
            self.todos,
            self.status,
        )
        try:
            self.todo_ids, self.todos, self.status = (
                filtered_ids,
                filtered_todos,
                filtered_status,
            )
            title = "Open todos" if show == "open" else "Completed todos"
            self._table_print(title=title)
        finally:
            self.todo_ids, self.todos, self.status = (
                original_ids,
                original_todos,
                original_status,
            )

    def remove_todo(self, index: int) -> None:
        # Maintain current UX: index refers to the displayed (1-based) ordering.
        self._check_and_load_todos(self.file_path_to_db)

        if index < 1 or index > len(self.todos):
            print("Error: Invalid todo index.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)

                row = conn.execute(
                    "SELECT id, item FROM todos ORDER BY id LIMIT 1 OFFSET ?;",
                    (index - 1,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo index.")
                    return

                todo_id, removed_item = row
                with conn:
                    conn.execute("DELETE FROM todos WHERE id = ?;", (todo_id,))
        except sqlite3.Error as e:
            print(f"Error: Failed to remove todo. ({e})")
            return

        print(f'Removed todo: "{removed_item}"')

    def clear_all(self) -> None:
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                with conn:
                    conn.execute("DELETE FROM todos;")
                    # Reset AUTOINCREMENT counter so ids start from 1 again.
                    # This is SQLite-specific and only applies to tables created with AUTOINCREMENT.
                    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'todos';")
        except sqlite3.Error as e:
            print(f"Error: Failed to clear todos. ({e})")
            return

        self.todo_ids = []
        self.todos = []
        self.status = []
        print("Cleared all todos.")

    def _check_and_load_todos(self, file_path: Path) -> None:
        # Create parent directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Optional one-time migration: if the user still has a legacy JSON file and
        # the DB is empty/new, import the items. This keeps upgrades smooth.
        json_path = file_path.with_suffix(".json")
        if json_path.exists() and file_path.suffix == ".db":
            migrate_from_json(json_path=json_path, db_path=file_path, backup=True)

        try:
            with sqlite3.connect(file_path) as conn:
                ensure_schema(conn)
                rows = conn.execute(
                    "SELECT id, item, done, created_at, done_at FROM todos ORDER BY id"
                ).fetchall()

                # In-memory lists are used by the interactive menu.
                self.todo_ids = [int(row[0]) for row in rows]
                self.todos = [row[1] for row in rows]
                self.status = [row[2] for row in rows]
        except sqlite3.Error as e:
            print(f"Warning: Failed to load existing todos. Starting fresh. ({e})")
            self.todo_ids = []
            self.todos = []
            self.status = []

    def _table_print(
        self,
        title: str | None = None,
        style: str = "bold cyan",
    ):
        table = Table(
            title=title, header_style=style, border_style=style, show_lines=True
        )
        columns = ["ID", "Todo Item", "Done"]
        for col in columns:
            table.add_column(str(col))

        for todo_id, todo, done in zip(
            self.todo_ids, self.todos, self.status, strict=False
        ):
            table.add_row(
                str(todo_id),
                str(todo),
                "[green]✔[/green]" if done else "[red]✖[/red]",
            )

        self._console.print(Padding(table, (2, 2)))

    def mark_as_not_done(self, index: int) -> None:
        self._check_and_load_todos(self.file_path_to_db)

        if index < 1 or index > len(self.todos):
            print("Error: Invalid todo index.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)

                row = conn.execute(
                    "SELECT id, item FROM todos ORDER BY id LIMIT 1 OFFSET ?;",
                    (index - 1,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo index.")
                    return

                todo_id, item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET done = 0, done_at = NULL WHERE id = ?;",
                        (todo_id,),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as not done. ({e})")
            return

        print(f'Marked todo as not done: "{item}"')

    def mark_as_done(self, index: int) -> None:
        self._check_and_load_todos(self.file_path_to_db)

        if index < 1 or index > len(self.todos):
            print("Error: Invalid todo index.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)

                row = conn.execute(
                    "SELECT id, item FROM todos ORDER BY id LIMIT 1 OFFSET ?;",
                    (index - 1,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo index.")
                    return

                todo_id, item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET done = ?, done_at = datetime('now') WHERE id = ?;",
                        (1, todo_id),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as done. ({e})")
            return

        print(f'Marked todo as done: "{item}"')

    def update_done_data(self, index, done_value, done_at_value, todo_id):
        text_done_value = "done" if done_value == 1 else "not done"
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)

                row = conn.execute(
                    "SELECT id, item FROM todos ORDER BY id LIMIT 1 OFFSET ?;",
                    (index - 1,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo index.")
                    return

                todo_id, item = row
                with conn:
                    if done_value:
                        conn.execute(
                            "UPDATE todos SET done = ?, done_at = datetime('now') WHERE id = ?;",
                            (1, todo_id),
                        )
                    else:
                        conn.execute(
                            "UPDATE todos SET done = ?, done_at = NULL WHERE id = ?;",
                            (0, todo_id),
                        )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as {text_done_value}. ({e})")
            return

    def edit_entry(self, index: int, new_text: str) -> None:
        self._check_and_load_todos(self.file_path_to_db)

        if index < 1 or index > len(self.todos):
            print("Error: Invalid todo index.")
            return

        new_text = (new_text or "").strip()
        if not new_text:
            print("Error: Todo item cannot be empty.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)

                row = conn.execute(
                    "SELECT id, item FROM todos ORDER BY id LIMIT 1 OFFSET ?;",
                    (index - 1,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo index.")
                    return

                todo_id, old_item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET item = ? WHERE id = ?;",
                        (new_text, todo_id),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to edit todo. ({e})")
            return

        print(f'Edited todo: "{old_item}" to "{new_text}"')

    def remove_by_id(self, todo_id: int) -> None:
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                row = conn.execute(
                    "SELECT id, item FROM todos WHERE id = ?;",
                    (todo_id,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo id.")
                    return

                _, removed_item = row
                with conn:
                    conn.execute("DELETE FROM todos WHERE id = ?;", (todo_id,))
        except sqlite3.Error as e:
            print(f"Error: Failed to remove todo. ({e})")
            return

        print(f'Removed todo: "{removed_item}"')

    def mark_done_by_id(self, todo_id: int) -> None:
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                row = conn.execute(
                    "SELECT id, item FROM todos WHERE id = ?;",
                    (todo_id,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo id.")
                    return

                _, item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET done = 1, done_at = datetime('now') WHERE id = ?;",
                        (todo_id,),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as done. ({e})")
            return

        print(f'Marked todo as done: "{item}"')

    def mark_not_done_by_id(self, todo_id: int) -> None:
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                row = conn.execute(
                    "SELECT id, item FROM todos WHERE id = ?;",
                    (todo_id,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo id.")
                    return

                _, item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET done = 0, done_at = NULL WHERE id = ?;",
                        (todo_id,),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as not done. ({e})")
            return

        print(f'Marked todo as not done: "{item}"')

    def edit_by_id(self, todo_id: int, new_text: str) -> None:
        new_text = (new_text or "").strip()
        if not new_text:
            print("Error: Todo item cannot be empty.")
            return

        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                row = conn.execute(
                    "SELECT id, item FROM todos WHERE id = ?;",
                    (todo_id,),
                ).fetchone()
                if row is None:
                    print("Error: Invalid todo id.")
                    return

                _, old_item = row
                with conn:
                    conn.execute(
                        "UPDATE todos SET item = ? WHERE id = ?;",
                        (new_text, todo_id),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to edit todo. ({e})")
            return

        print(f'Edited todo: "{old_item}" to "{new_text}"')
