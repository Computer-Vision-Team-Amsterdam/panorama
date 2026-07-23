#!/bin/bash
set -e

uv run isort panorama tests
uv run black .
uv run mypy --config-file=.mypyrc panorama tests
uv run pylint --jobs=0 --rcfile=.pylintrc panorama tests
uv run pytest -s --cov=panorama --cov-report html --cov-report term-missing
(cd docs && uv run make html)
