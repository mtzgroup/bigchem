# BigQC

A distributed system for scaling and parallelizing quantum chemistry calculations.

## Getting Started

Install project dependencies using [poetry](https://python-poetry.org/)

```sh
poetry install
```

Check that your installation is working correctly by running the test. (Requires docker-compose).

```sh
sh scripts/test.sh
```

You can review test coverage in the now-generated `htmlcov` folder; open `index.html` in a browser.

Run the following commands to startup a broker, backend, and worker.

```sh
docker-compose up -d --build
```

Then run the following script to see an example of how to submit a computation and retrieve its result.

```sh
poetry run python -m scripts.example
```
