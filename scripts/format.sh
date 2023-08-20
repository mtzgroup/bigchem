#!/bin/sh -e

set -x

poetry run black .
poetry run isort .
poetry run ruff check --fix .
