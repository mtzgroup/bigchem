#!/bin/sh

set -xe

docker push mtzgroup/bigchem-worker:$(poetry version -s)
docker push mtzgroup/bigchem-worker:latest
docker push mtzgroup/bigchem-worker:$(poetry version -s)-terachem
docker push mtzgroup/bigchem-worker:latest-terachem