from __future__ import annotations

from argparse import ArgumentParser
from cli_todo_jd.main import (
    add_item_to_list,
    remove_item_from_list,
    list_items_on_list,
    clear_list_of_items,
    cli_menu,
    mark_item_as_done,
    mark_item_as_not_done,
)
from pathlib import Path
import typer

app = typer.Typer(help="A tiny todo CLI built with Typer.")


@app.command()
def add(
    text: list[str] = typer.Argument(..., help="Todo item text (no quotes needed)."),
    filepath: Path = typer.Option(
        Path(".todo_list.db"),
        "--filepath",
        "-f",
        help="Path to the JSON file used for storage.",
    ),
) -> None:
    full_text = " ".join(text).strip()
    if not full_text:
        raise typer.BadParameter("Todo item text cannot be empty.")

    add_item_to_list(full_text, filepath)
    typer.echo(f"Added: {full_text}")


@app.command(name="list")
def list_(
    filepath: Path = typer.Option(Path(".todo_list.db"), "--filepath", "-f"),
) -> None:
    list_items_on_list(filepath)


@app.command()
def remove(
    index: int = typer.Argument(..., help="1-based index of item to remove."),
    filepath: Path = typer.Option(Path(".todo_list.db"), "--filepath", "-f"),
) -> None:
    remove_item_from_list(index, filepath)


@app.command()
def clear(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    filepath: Path = typer.Option(Path(".todo_list.db"), "--filepath", "-f"),
) -> None:
    if not yes and not typer.confirm(f"Clear all todos in {filepath}?"):
        typer.echo("Cancelled.")
        raise typer.Exit(code=1)

    clear_list_of_items(filepath)


@app.command(name="menu")
def menu_(
    filepath: Path = typer.Option(
        Path(".todo_list.db"),
        "--filepath",
        "-f",
        help="Path to the JSON file used for storage.",
    ),
) -> None:
    cli_menu(filepath)
    typer.echo("Exited menu.")


@app.command()
def done(
    index: int = typer.Argument(..., help="1-based index of item to mark as done."),
    filepath: Path = typer.Option(Path(".todo_list.db"), "--filepath", "-f"),
) -> None:
    mark_item_as_done(index, filepath)
    list_(filepath=filepath)


@app.command()
def not_done(
    index: int = typer.Argument(..., help="1-based index of item to mark as done."),
    filepath: Path = typer.Option(Path(".todo_list.db"), "--filepath", "-f"),
) -> None:
    mark_item_as_not_done(index, filepath)
    list_(filepath=filepath)


def parser_optional_args(parser: ArgumentParser):
    parser.add_argument(
        "-f",
        "--filepath",
        help="Path to the file to process",
        default="./.todo_list.db",
    )


def todo_menu():
    parser = ArgumentParser(description="Todo List CLI Menu")
    parser_optional_args(parser)
    args = parser.parse_args()

    cli_menu(filepath=args.filepath)


if __name__ == "__main__":
    app()
