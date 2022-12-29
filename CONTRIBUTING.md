# Contributing to *flywheel-utilities*

## Bug reporting

If you believe you've found a bug, please open a new Github Issue and provide as much detail as possible.

## Code contributions

Code contributions are very welcome. Code must not be committed directly to `main`. 
Instead, create a new branch based on `main` and initiate a pull request.

Before committing your code, check that it will pass the automated CI tests.
To run the tests locally before committing,
run the following commands from the root of this repository and ensure all tests pass:
```
  $ pytest -v tests
  $ ./check_formatting.sh
```
The tests you will require packages listed in the `requirements_dev.txt` file.


## Coding conventions

To ensure consistency across the code base, this project uses the following linters and formatters:
- pylint
- mypy
- isort
- black

The only significant deviation from the default settings is the accepted line width which is set at 100.
To see all arguments passed to the above linters/formatters, see the tool sections in the `pyproject.toml` file.
