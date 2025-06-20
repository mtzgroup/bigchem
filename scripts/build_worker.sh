#!/bin/sh
# Run this script with sh scripts/build_worker.sh to build the worker without TeraChem
# Run this script with sh scripts/build_worker.sh --terachem to build the worker with TeraChem

# Workers get built tagged with the current version of bigchem
# Non TeraChem workers get tagged as ":latest" (very large image with TeraChem)
# TeraChem workers get an additional -terachem tag

set -xe

BASE_IMAGE=""
IMAGE_TAG="-t mtzgroup/bigchem-worker:$(uv run hatch version)"
TAG_LATEST="-t mtzgroup/bigchem-worker:latest"

# Parse command line options
for arg in "$@"; do
    case $arg in
    --terachem)
        BASE_IMAGE="--build-arg BASE_IMAGE=mtzgroup/terachem:latest"
        IMAGE_TAG="-t mtzgroup/bigchem-worker:$(uv run hatch version)-terachem"
        TAG_LATEST="-t mtzgroup/bigchem-worker:latest-terachem"
        ;;
    esac
done

# Build the docker image
docker build $IMAGE_TAG $TAG_LATEST $BASE_IMAGE -f docker/worker.dockerfile .
