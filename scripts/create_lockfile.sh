#! /bin/bash
# Create env.lock for workers from env.yaml file
# This will potentially upgrade the packages used in the worker

cd docker

docker run -it --rm -v $(pwd):/tmp mambaorg/micromamba:1.4-jammy \
    /bin/bash -c "micromamba create --yes --name new_env --file env.yaml && \
                 micromamba env export --name new_env --explicit > env.lock"

cd ..
