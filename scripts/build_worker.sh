#!/bin/sh

set -xe

docker build -t coltonbh/bigchem-worker:$(poetry version -s) -t coltonbh/bigchem-worker:latest -f docker/worker.dockerfile .