#!/bin/sh -e

set -x

poetry run ruff check --fix .
