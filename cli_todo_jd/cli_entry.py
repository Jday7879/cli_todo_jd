from argparse import ArgumentParser
from cli_todo_jd.main import (
    add_item_to_list,
    remove_item_from_list,
    list_items_on_list,
    clear_list_of_items,
    cli_menu,
)


def parser_optional_args(parser: ArgumentParser):
    parser.add_argument(
        "-f",
        "--filepath",
        help="Path to the file to process",
        default="./.todo_list.json",
    )


def add_item():
    parser = ArgumentParser(description="Add a todo item")
    parser.add_argument(
        "item",
        nargs="+",
        help="The todo item to add (use quotes or multiple words)",
    )
    parser_optional_args(parser)

    args = parser.parse_args()
    args.item = " ".join(args.item)
    add_item_to_list(args.item, args.filepath)


def remove_item():
    parser = ArgumentParser(description="Remove a todo item by index")
    parser.add_argument(
        "index",
        type=int,
        help="The index of the todo item to remove (1-based)",
    )
    parser_optional_args(parser)

    args = parser.parse_args()
    remove_item_from_list(args.index, args.filepath)


def list_items():
    parser = ArgumentParser(description="List all todo items")
    parser_optional_args(parser)

    args = parser.parse_args()
    list_items_on_list(args.filepath)


def clear_list():
    parser = ArgumentParser(description="Clear all todo items")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not prompt for confirmation",
    )
    parser_optional_args(parser)

    args = parser.parse_args()
    list_items_on_list(args.filepath)

    if not args.yes:
        resp = (
            input(f"Clear all todo items in '{args.filepath}'? [y/n]: ").strip().lower()
        )
        if resp not in ("y", "yes"):
            return

    # assuming remove_item_from_list(0/None) clears; otherwise replace with your clear implementation
    clear_list_of_items(args.filepath)


def todo_menu():
    parser = ArgumentParser(description="Todo List CLI Menu")
    parser_optional_args(parser)
    args = parser.parse_args()

    cli_menu(filepath=args.filepath)
