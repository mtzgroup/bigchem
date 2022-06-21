#!/bin/sh

set -xe

docker build -t coltonbh/bigqc-worker:$(poetry version -s) -t coltonbh/bigqc-worker:latest -f docker/worker.dockerfile .