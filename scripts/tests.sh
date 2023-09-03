#!/bin/sh

set -xe

# Start docker redis, rabbitmq, and psi4 celery worker containers
docker compose up -d --build

# Run tests and capture the exit status
poetry run pytest --cov-report=term-missing --cov-report html:htmlcov --cov-config=pyproject.toml --cov=bigchem --cov=tests . || TEST_EXIT_CODE=$?

# Stop docker containers
docker compose down

# Exit with the pytest status (will be 0 if pytest was successful, and some other value otherwise)
exit ${TEST_EXIT_CODE:-0}
