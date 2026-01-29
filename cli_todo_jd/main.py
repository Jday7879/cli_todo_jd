from pathlib import Path
import questionary
from rich.console import Console
from rich.table import Table
from rich.padding import Padding
import sqlite3

from cli_todo_jd.storage.schema import ensure_schema
from cli_todo_jd.storage.migrate import migrate_from_json


def main():
    TodoApp()


class TodoApp:
    """
    A simple command-line todo application.
    """

    def __init__(self, file_path_to_db="./.todo_list.db"):
        self.todos = []
        self.status = []
        self.file_path_to_db = Path(file_path_to_db)
        self._check_and_load_todos(self.file_path_to_db)
        self._console = Console()

    def add_todo(self, item: str) -> None:
        item = (item or "").strip()
        if not item:
            print("Error: Todo item cannot be empty.")
            return

        try:
            with sqlite3.connect(self.file_path_to_json) as conn:
                ensure_schema(conn)
                with conn:
                    conn.execute(
                        "INSERT INTO todos(item, done) VALUES (?, 0);", (item,)
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to add todo. ({e})")
            return

        print(f'Added todo: "{item}"')
        self._check_and_load_todos(self.file_path_to_db)

    def list_todos(self) -> None:
        # Always read fresh so output reflects the DB
        self._check_and_load_todos(self.file_path_to_db)
        if not self.todos:
            print("No todos found.")
            return
        self._table_print()

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
        self._check_and_load_todos(self.file_path_to_db)

    def clear_all(self) -> None:
        try:
            with sqlite3.connect(self.file_path_to_db) as conn:
                ensure_schema(conn)
                with conn:
                    conn.execute("DELETE FROM todos;")
        except sqlite3.Error as e:
            print(f"Error: Failed to clear todos. ({e})")
            return

        self.todos = []
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

                # In-memory list is used by the interactive menu for selection.
                # Keep it as a simple list[str] for now.
                self.todos = [row[1] for row in rows]
                self.status = [row[2] for row in rows]
        except sqlite3.Error as e:
            print(f"Warning: Failed to load existing todos. Starting fresh. ({e})")
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

        for idx, todo in enumerate(self.todos, start=1):
            table.add_row(
                f"{idx}.",
                str(todo),
                "[green]✔[/green]" if self.status[idx - 1] else "[red]✖[/red]",
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
        self._check_and_load_todos(self.file_path_to_db)

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
                        "UPDATE todos SET done = 1, done_at = datetime('now') WHERE id = ?;",
                        (todo_id,),
                    )
        except sqlite3.Error as e:
            print(f"Error: Failed to mark todo as done. ({e})")
            return

        print(f'Marked todo as done: "{item}"')
        self._check_and_load_todos(self.file_path_to_db)


def create_list(file_path_to_db: str = "./.todo_list.db"):
    """
    Create a new todo list.

    Parameters
    ----------
    file_path_to_json : str, optional
        The file path to the JSON file for storing todos, by default "./.todo_list.db"

    Returns
    -------
    TodoApp
        An instance of the TodoApp class.
    """
    app = TodoApp(file_path_to_db=file_path_to_db)
    return app


def add_item_to_list(item: str, filepath: str):
    """
    Add a new item to the todo list.

    Parameters
    ----------
    item : str
        The todo item to add.
    filepath : str
        The file path to the JSON file for storing todos.
    """
    app = create_list(file_path_to_db=filepath)
    app.add_todo(item)
    app.list_todos()
    app.write_todos()


def list_items_on_list(filepath: str):
    """
    List all items in the todo list.

    Parameters
    ----------
    filepath : str
        The file path to the JSON file for storing todos.
    """
    app = create_list(file_path_to_db=filepath)
    app.list_todos()


def remove_item_from_list(index: int, filepath: str):
    """
    remove an item from the todo list using index

    Parameters
    ----------
    index : int
        The index of the todo item to remove.
    filepath : str
        The file path to the JSON file for storing todos.
    """
    app = create_list(file_path_to_db=filepath)
    app.remove_todo(index)
    app.list_todos()
    app.write_todos()


def clear_list_of_items(filepath: str):
    """
    Clear all items from the todo list.

    Parameters
    ----------
    filepath : str
        The file path to the JSON file for storing todos.
    """
    app = create_list(file_path_to_db=filepath)
    app.clear_all()


def cli_menu(filepath="./.todo_list.db"):
    """
    Display the command-line interface menu for the todo list.

    Parameters
    ----------
    filepath : str, optional
        The file path to the JSON file for storing todos, by default "./.todo_list.db"
    """
    app = create_list(file_path_to_db=filepath)
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Add todo",
                "List todos",
                "Remove todo",
                "Clear all todos",
                "Exit",
            ],
        ).ask()

        if action == "Add todo":
            item = questionary.text("Enter the todo item:").ask()
            app.add_todo(item)
        elif action == "List todos":
            app.list_todos()
        elif action == "Remove todo":
            if not app.todos:
                print("No todos to remove.")
                continue
            todo_choice = questionary.select(
                "Select the todo to remove:",
                choices=["<Back>"] + app.todos,
            ).ask()

            if todo_choice == "<Back>":
                continue

            todo_to_remove = app.todos.index(todo_choice) + 1
            app.remove_todo(todo_to_remove)

        elif action == "Clear all todos":
            confirm = questionary.confirm(
                "Are you sure you want to clear all todos?"
            ).ask()
            if confirm:
                app.clear_all()
        elif action == "Exit":
            break
        else:
            break


if __name__ == "__main__":
    TodoApp().mark_as_not_done(1)
    TodoApp().list_todos()
    TodoApp().mark_as_done(1)
    TodoApp().list_todos()
