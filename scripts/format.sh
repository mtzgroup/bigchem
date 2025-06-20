#!/bin/sh -e

set -x

uv run ruff check --fix .
