# Python Template Repository

This template provides a boilerplate repository for developing Python-based project.

## Installation

### Requirements

Make sure your `.pip/pip.conf` file contains the `--index-url` option with your
JFrog credentials

```bash
[global]
index-url = https://<username>:<key>@flyability.jfrog.io/artifactory/api/pypi/pypi-virtual/simple
```

### User

Create a new virtual environment and source it (you can also use an existing one):

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Installing package locally:

```bash
python3 -m pip install .
```

Then, from anywhere on your system, you can use the scripts declared in
`pyproject.toml` in `[project.scripts]`. For example:

```bash
python_template_repository_dummy
```

### Developer

You can use the `python -m pip install -e .` option to install in editable mode.

To install the tools for development (listed in `pyproject.toml` under
`[project.optional-dependencies]`), use:

```bash
python3 -m pip install .[dev]
```

## Documentation

Run the following command to build the `python_template_repository` documentation from
the root of the repository:

```bash
( cd docs; rm -fr _build _autosummary; sphinx-build -M  html . _build -W --keep-going && sphinx-build -M linkcheck . _build )
```

To build quickly the documentation, you can run:

```bash
sphinx-build -M html docs docs/_build -W --keep-going
```

This will be much faster, but it will not guarantee that all the documentation is up to
date or that all links are reachable.

Open the HTML documentation with your default browser:
`sensible-browser docs/_build/html/index.html`

## Code quality

To improve Python code quality, the following frameworks have been chosen:

* [black](https://black.readthedocs.io/en/stable/): tool to format Python code
* [mypy](https://github.com/python/mypy): static type checker for Python.
  See the config in `pyproject.toml`.
  * [PEP 484 -- Type Hint](https://www.python.org/dev/peps/pep-0484/): a Python
      Enhancement Proposal providing a standard syntax for type annotations.
  * [Type hints cheat sheet (Python 3)](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html):
      shows how the PEP 484 type annotation notation represents various common types
      in Python 3.
* [pytest](https://docs.pytest.org/en/latest/): automated tests framework that supports unittest
* [ruff](https://beta.ruff.rs/docs/): extremely fast Python linter, written in Rust.
  The rules selected are very close to flake8 + isort.
* [pydoclint](https://github.com/jsh9/pydoclint): docstring analysis

These tools are run automatically for each pull-request.

### Run manually

To test and format manually the code quality, go at the root of `python_template_repository`
project:

* Formatter: `black .`
* Linter: `ruff check .`
* Document linter: `pydoclint .`
* Static type checker: `mypy --install-types --non-interactive .`
* Unit testing: `pytest`

You might want to check out [pydocstyle](http://www.pydocstyle.org/en/stable/) to help you
with the formatting of pyyour documentation as well.

## Docstrings

All modules, classes, methods, and functions should have a docstring.

All docstrings should have a resuming sentence (ending with a '.') on the first line.

The docstrings style is the [standard sphinx style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html#the-sphinx-docstring-format).

## python_template_repository base structure

 python_template_repository structure with one `dummy` module using as example:

```bash
.
├── docs
│   ├── conf.py
│   ├── nitpick-exceptions
│   ├── _static
│   │   └── css
│   │       └── custom.css
│   ├── _templates
│   ├── index.rst
│   ├── api.rst
│   └── usage
│       └── installation.rst
├── src
│   ├── python_template_repository
│   │   ├── __init__.py
│   │   ├── package
│   │   │   ├── __init__.py
│   │   │   └── module.py
│   │   ├── scripts
│   │   │   ├── __init__.py
│   │   │   └── script.py
│   │   └── other_module.py
├── tests
│   └── package
│       └── test_module.py
├── README.md
├── pyproject.toml
├── .gitignore
├── .readthedocs.yaml
└── sonar-project.properties
```
