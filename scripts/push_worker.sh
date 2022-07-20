#!/bin/sh

set -xe

docker push coltonbh/bigchem-worker:$(poetry version -s)
docker push coltonbh/bigchem-worker:latest
