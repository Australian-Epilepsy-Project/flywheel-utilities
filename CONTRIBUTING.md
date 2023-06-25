# Contributing to *flywheel-utilities*

## Bug reporting

If you believe you've found a bug, please open a new Github Issue and provide as much detail as possible.

## Code contributions

Code contributions are very welcome. Code must not be committed directly to `main`.
Instead, either for the repository or create a new branch based on `dev` and initiate a pull request onto `dev`.

Before committing your code, make sure `pre-commit` is installed (dev option).
This will ensure the following linters/formatters are run over each commit.
- pylint
- mypy
- isort
- black
- codespell

The only significant deviation from the default settings is the accepted line width which is set at 100.
To see all arguments passed to the above linters/formatters, see the tool sections in the `pyproject.toml` file.
