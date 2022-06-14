#!/bin/sh

set -xe

docker build -t coltonbh/bigqc-worker:$(poetry version -s) -f docker/worker.dockerfile .