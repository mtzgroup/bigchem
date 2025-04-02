#! /bin/bash
# Create env.lock for workers from env.yaml file
# This will potentially upgrade the packages used in the worker

set -x

cd docker

docker run -it --rm -u $(id -u):$(id -g) -v $(pwd):/tmp mambaorg/micromamba:1.5-noble \
    /bin/bash -c "micromamba create --yes --name new_env --file env.yaml && \
                 micromamba env export --name new_env --explicit > env.lock"

cd ..
