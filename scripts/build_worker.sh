#!/bin/sh

set -xe

docker build -t mtzgroup/bigchem-worker:$(poetry version -s) -t mtzgroup/bigchem-worker:latest -f docker/worker.dockerfile .