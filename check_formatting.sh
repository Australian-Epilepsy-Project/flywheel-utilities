#!/bin/bash
##############################################################################################
# Run all linters and formatters over python package
# isort and black run with --check/--diff flag so files will NOT be altered

echo "Running linters and formatters over package"

DIR_CHECK=flywheel_utilities

# pylint
echo "Running pylint...."
pylint "${DIR_CHECK}"
RET_PYLINT=$?

# isort
echo "Running isort...."
isort --check "${DIR_CHECK}"
RET_ISORT=$?

# mypy
echo "Running mypy...."
mypy "${DIR_CHECK}"
RET_MYPY=$?

# black
echo "Running black...."
black --diff "${DIR_CHECK}"
RET_BLACK=$?

# Summarize which failed
echo ""
echo "-------------------------------------------------------"
RET_FINAL=0
if [[ "${RET_PYLINT}" -ne 0 ]]; then
  echo "- pylint failed"
  RET_FINAL=1
fi
if [[ "${RET_ISORT}" -ne 0 ]]; then
  echo "- isort failed"
  RET_FINAL=1
fi
if [[ "${RET_MYPY}" -ne 0 ]]; then
  echo "- mypy failed"
  RET_FINAL=1
fi
if [[ "${RET_BLACK}" -ne 0 ]]; then
  echo "- black failed"
  RET_FINAL=1
fi

if [[ ${RET_FINAL} -eq 0 ]]; then
  echo "All formatting and linting test passed!"
fi

exit ${RET_FINAL}
