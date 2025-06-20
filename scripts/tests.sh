#!/bin/sh

set -xe

# Start docker redis, rabbitmq, and BigChem worker containers
docker compose up -d --build --wait --wait-timeout 60

echo "Waiting for services to start..."
sleep 5
# Run tests and capture the exit status
uv run pytest -vv --cov-report=term-missing --cov-report html:htmlcov --cov-config=pyproject.toml --cov=src/bigchem --cov=tests . || TEST_EXIT_CODE=$?

# Stop docker containers
docker compose down

# Exit with the pytest status (will be 0 if pytest was successful, and some other value otherwise)
exit ${TEST_EXIT_CODE:-0}
