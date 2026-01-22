import json
from pathlib import Path
import questionary
from rich.console import Console
from rich.table import Table
from rich.padding import Padding


def main():
    TodoApp()


class TodoApp:
    def __init__(self, file_path_to_json="./.cli_todo.json"):
        self.todos = []
        self.file_path_to_json = Path(file_path_to_json)
        self._check_and_load_todos(self.file_path_to_json)
        self._console = Console()

    def add_todo(self, item):
        self.todos.append(item)
        print(f'Added todo: "{item}"')

    def list_todos(self):
        if not self.todos:
            print("No todos found.")
            return
        self._table_print()

    def remove_todo(self, index):
        try:
            removed = self.todos.pop(index - 1)
            print(f'Removed todo: "{removed}"')
        except IndexError:
            print("Error: Invalid todo index.")

    def _check_and_load_todos(self, file_path):
        if file_path.exists():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    self.todos = json.load(f)
            except (json.JSONDecodeError, OSError):
                print("Warning: Failed to load existing todos. Starting fresh.")

    def write_todos(self):
        try:
            with self.file_path_to_json.open("w", encoding="utf-8") as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Warning: failed to save todos: {e}")

    def _table_print(
        self,
        title: str | None = "Todo List",
        style: str = "bold cyan",
    ):
        table = Table(
            title=title, header_style=style, border_style=style, show_lines=True
        )
        columns = ["ID", "Todo Item"]
        for col in columns:
            table.add_column(str(col))
        for idx, todo in enumerate(self.todos, start=1):
            table.add_row(f"{idx}.", todo)
        self._console.print(Padding(table, (2, 2)))


def create_list(file_path_to_json="./.cli_todo.json"):
    app = TodoApp(file_path_to_json=file_path_to_json)
    return app


def add_item_to_list(item, filepath):
    app = create_list(file_path_to_json=filepath)
    app.add_todo(item)
    app.list_todos()
    app.write_todos()


def list_items_on_list(filepath):
    app = create_list(file_path_to_json=filepath)
    app.list_todos()


def remove_item_from_list(index, filepath):
    app = create_list(file_path_to_json=filepath)
    app.remove_todo(index)
    app.list_todos()
    app.write_todos()


def clear_list_of_items(filepath):
    app = create_list(file_path_to_json=filepath)
    app.todos = []
    print("Cleared all todos.")
    app.write_todos()


def cli_menu(filepath="./.cli_todo.json"):
    app = create_list(file_path_to_json=filepath)
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
            app.write_todos()
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
            app.write_todos()

        elif action == "Clear all todos":
            confirm = questionary.confirm(
                "Are you sure you want to clear all todos?"
            ).ask()
            if confirm:
                app.todos = []
                print("Cleared all todos.")
                app.write_todos()
        elif action == "Clear all todos":
            confirm = questionary.confirm(
                "Are you sure you want to clear all todos?"
            ).ask()
            if confirm:
                app.todos = []
                print("Cleared all todos.")
                app.write_todos()
        elif action == "Exit":
            break
        else:
            break


if __name__ == "__main__":
    # # Persist todos to a JSON file in the user's home directory.
    # app = create_app()
    # # Example usage
    # app.add_todo("Buy milk")
    # app.add_todo("Read a book")
    # app.list_todos()
    # app.remove_todo(3)
    # app.remove_todo(3)
    # app.list_todos()
    # app.write_todos()
    # cli_menu()
    app = create_list()
    app.list_todos()
