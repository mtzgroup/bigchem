#!/bin/sh

set -x

# Start docker redis, rabbitmq, and psi4 celery worker containers
docker compose up -d --build

# Run tests
poetry run pytest --cov-report=term-missing --cov-report html:htmlcov --cov-config=pyproject.toml --cov=bigchem --cov=tests .

# Stop docker containers
docker compose down
