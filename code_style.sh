#!/bin/bash
set -e

poetry run isort panorama tests
poetry run black .
poetry run mypy --config-file=.mypyrc panorama tests
poetry run pylint --rcfile=.pylintrc panorama tests
poetry run pytest -s --cov=panorama --cov-report html
