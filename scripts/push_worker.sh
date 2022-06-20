#!/bin/sh

set -xe

docker push coltonbh/bigqc-worker:$(poetry version -s)
docker push coltonbh/bigqc-worker:latest
