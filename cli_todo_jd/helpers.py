from cli_todo_jd.main import TodoApp


def create_list(file_path_to_db: str = "./.todo_list.db"):
    """
    Create a new todo list.

    Parameters
    ----------
    file_path_to_db : str, optional
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


def list_items_on_list(filepath: str, show: str = "open"):
    """List items in the todo list.

    Parameters
    ----------
    filepath:
        The SQLite database path.
    show:
        "open" (default), "done", or "all".
    """
    app = create_list(file_path_to_db=filepath)
    app.list_todos(show=show)


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


def mark_item_as_done(index: int, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.mark_as_done(index)


def mark_item_as_not_done(index: int, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.mark_as_not_done(index)


def remove_item_from_list_by_id(todo_id: int, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.remove_by_id(todo_id)
    app.list_todos(show="all")


def mark_item_as_done_by_id(todo_id: int, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.mark_done_by_id(todo_id)


def mark_item_as_not_done_by_id(todo_id: int, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.mark_not_done_by_id(todo_id)


def edit_item_in_list_by_id(todo_id: int, new_text: str, filepath: str):
    app = create_list(file_path_to_db=filepath)
    app.edit_by_id(todo_id, new_text)
