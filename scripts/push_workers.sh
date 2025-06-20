#!/bin/sh

set -xe

docker push mtzgroup/bigchem-worker:$(uv run hatch version)
docker push mtzgroup/bigchem-worker:latest
docker push mtzgroup/bigchem-worker:$(uv run hatch version)-terachem
docker push mtzgroup/bigchem-worker:latest-terachem