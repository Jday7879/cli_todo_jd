# cli-todo-jd

A command line to do list with interactive menu

## What is`cli-todo-jd`?

This is a command line interface todo list. Once installed, there are two ways to interact 
with the list. 

### `todo-menu`

Once installed us `todo_menu` to launch into the interactive menu. From here you can add,
remove, list, or clear your todo list. Items in your list are stored (by default) as
`.todo_list.json`. The menu does also support optional filepaths using `-f` or `--filepath`.


### interacting with todo list without menu

Alternatly you can interact directly using the following commands (`--filepath can be substituted for -f`)

- `todo_add text --filepath optional_path_to_json` used to add an item to your list
- `todo_remove index --filepath optional_path_to_json` used to remove item number `index`
- `todo_list --filepath optional_path_to_json` used to view list
- `todo_clear --filepath optional_path_to_json` used to clear list (prompts y/n to confirm)

## Getting started

To start using this project, first make sure your system meets its
requirements.

It's suggested that you install this package and its requirements within
a virtual environment.

## Requirements

- Python 3.9+ installed

## Installing the package

Whilst in the root folder, in a terminal, you can install the package and its
Python dependencies using:

```shell
python -m pip install -U pip setuptools
pip install -e .
```

### Install for contributors/developers

To install the contributing requirements, use:
```shell
python -m pip install -U pip setuptools
pip install -e .[dev]
pre-commit install
```

This installs an editable version of the package. This means that when you update the
package code you do not have to reinstall it for the changes to take effect.
This saves a lot of time when you test your code.

Remember to update the setup and requirement files inline with any changes to your
package.


## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers
both the codebase and any sample code in the documentation.

## Contributing

If you want to help us build and improve `{{ cookiecutter.project_slug }}`, please take a look at our
[contributing guidelines][contributing].

## Acknowledgements

This project structure is based on the [`govcookiecutter` template project][govcookiecutter].

[contributing]: https://github.com/best-practice-and-impact/govcookiecutter/blob/main/%7B%7B%20cookiecutter.repo_name%20%7D%7D/docs/contributor_guide/CONTRIBUTING.md
[govcookiecutter]: https://github.com/best-practice-and-impact/govcookiecutter