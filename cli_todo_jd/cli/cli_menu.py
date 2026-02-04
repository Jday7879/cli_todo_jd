from questionary import Style
import questionary
from cli_todo_jd.helpers import create_list

custom_style = Style(
    [
        ("qmark", "fg:#ff9d00 bold"),
        ("question", "bold"),
        ("answer", "fg:#ff9d00 bold"),
        ("pointer", "fg:#ff9d00 bold"),
        ("highlighted", "fg:#ff9d00 bold"),
        ("selected", "fg:#ff9d00 bold"),
        ("separator", "fg:#ff9d00 bold"),
        ("instruction", ""),  # default
        ("text", ""),
        ("disabled", "fg:#ff9d00 italic"),
    ]
)


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
                "Update todo status",
                "Remove todo",
                "Edit todo",
                "Clear all todos",
                "Exit",
            ],
            style=custom_style,
        ).ask()

        if action == "Add todo":
            item = questionary.text("Enter the todo item:", style=custom_style).ask()
            app.add_todo(item)
        elif action == "List todos":
            app.list_todos(show="all")
        elif action == "Update todo status":
            app.reload_todos()
            if not app.todos:
                print("No todos to update.")
                continue
            todo_choice = questionary.select(
                "Select the todo to update:",
                choices=["<Back>"] + app.todos,
                style=custom_style,
            ).ask()

            if todo_choice == "<Back>" or todo_choice is None:
                continue

            todo_index = app.todos.index(todo_choice) + 1
            status_choice = questionary.select(
                "Mark as:",
                choices=["Done", "Not Done", "<Back>"],
                style=custom_style,
            ).ask()

            if status_choice == "<Back>" or status_choice is None:
                continue
            elif status_choice == "Done":
                app.mark_as_done(todo_index)
            elif status_choice == "Not Done":
                app.mark_as_not_done(todo_index)
            app.list_todos(show="all")
        elif action == "Remove todo":
            app.reload_todos()
            if not app.todos:
                print("No todos to remove.")
                continue
            todo_choice = questionary.select(
                "Select the todo to remove:",
                choices=["<Back>"] + app.todos,
                style=custom_style,
            ).ask()

            if todo_choice == "<Back>" or todo_choice is None:
                continue

            todo_to_remove = app.todos.index(todo_choice) + 1
            app.remove_todo(todo_to_remove)
        elif action == "Edit todo":
            app.reload_todos()
            if not app.todos:
                print("No todos to edit.")
                continue
            todo_choice = questionary.select(
                "Select the todo to edit:",
                choices=["<Back>"] + app.todos,
                style=custom_style,
            ).ask()

            if todo_choice == "<Back>" or todo_choice is None:
                continue

            todo_index = app.todos.index(todo_choice) + 1
            new_text = questionary.text(
                "Enter the new text for the todo:",
                default=todo_choice,
                style=custom_style,
            ).ask()

            if new_text is None:
                continue
            app.edit_entry(todo_index, new_text)

        elif action == "Clear all todos":
            confirm = questionary.confirm(
                "Are you sure you want to clear all todos?", style=custom_style
            ).ask()
            if confirm:
                app.clear_all()
        elif action == "Exit":
            break
        else:
            break
