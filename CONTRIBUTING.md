# Contributing to *flywheel-utilities*

## Bug reporting

If you believe you've found a bug, please open a new Github Issue and provide as much detail as possible.

## Code contributions

Code contributions are very welcome. Code must not be committed directly to `main`.
Instead, either fork the repository or create a new branch based from `dev` and initiate a pull request onto `dev`.

To ensure consistent coding conventions, make sure [pre-commit](https://pre-commit.com/) is installed.
To install all `dev` dependencies (in editable mode for development), including `pre-commit`, use the following command:
```
  $ python3 -m pip install -e .[dev]
```
and then run
```
  $ pre-commit install
```
from the root of this repository.
To test that you have installed everything correctly, run:
```
  $ pytest -vv
```

Now when committing code, `pre-commit` will ensure the following linters/formatters are run over each commit.
- pylint
- mypy
- isort
- black
- codespell

The only significant deviation from the default settings is the accepted line width which is set at 100.
To see all arguments passed to the above linters/formatters, see the tool sections in the `pyproject.toml` file.
