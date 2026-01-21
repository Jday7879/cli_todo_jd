import json
from pathlib import Path

def main():
    TodoApp()
    
class TodoApp:
    def __init__(self):
        self.todos = []

    def add_todo(self, item):
        self.todos.append(item)
        print(f'Added todo: "{item}"')

    def list_todos(self):
        if not self.todos:
            print("No todos found.")
            return
        print("Your todos:")
        for idx, todo in enumerate(self.todos, start=1):
            print(f"{idx}. {todo}")


if __name__ == "__main__":
    # Persist todos to a JSON file in the user's home directory.
    data_file = Path.home() / ".cli_todo.json"

    # Load existing todos (if any)
    if data_file.exists():
        try:
            todos = json.loads(data_file.read_text(encoding="utf-8"))
            if isinstance(todos, list):
                app = TodoApp()
                app.todos = todos
            else:
                app = TodoApp()
        except (json.JSONDecodeError, OSError):
            app = TodoApp()
    else:
        app = TodoApp()

    # Example usage
    app.add_todo("Buy groceries")
    app.list_todos()

    # Save todos back to disk
    try:
        data_file.write_text(json.dumps(app.todos, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"Warning: failed to save todos: {e}")
