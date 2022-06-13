set -x

# Start docker redis, rabbitmq, and psi4 celery worker containers
docker-compose up -d --build

# Run tests
poetry run pytest --cov-report html:htmlcov --cov -v

# Stop docker containers
docker-compose down
