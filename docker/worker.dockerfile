# Base image with micromamba for QC programs
ARG BASE_IMAGE=mambaorg/micromamba:1.5-noble
FROM $BASE_IMAGE

LABEL maintainer="Colton Hicks <colton@coltonhicks.com>"

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Use system python, no need for venv
    UV_PROJECT_ENVIRONMENT=/opt/conda \
    # Improves startup time
    UV_COMPILE_BYTECODE=1

# Perform root tasks
WORKDIR /opt/
USER root
RUN apt-get update && \
    # for psutil in qcengine
    # https://github.com/giampaolo/psutil/blob/master/INSTALL.rst
    apt-get install -y gcc python3-dev curl && \
    chown -R $MAMBA_USER /opt/
USER $MAMBA_USER

# Install QC Programs
COPY --chown=$MAMBA_USER:$MAMBA_USER docker/env.lock ./
RUN micromamba install -y -n base -f env.lock && \
    micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Copy in latest uv binaries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy in project metadata and lock file
COPY --chown=$MAMBA_USER:$MAMBA_USER pyproject.toml LICENSE uv.lock README.md ./

# Install only main dependencies (no dev groups); don't remove existing packages
RUN uv sync --inexact --locked --no-install-project --no-dev --all-extras

# Copy source code (src layout)
COPY --chown=$MAMBA_USER:$MAMBA_USER src/ src/

# Install Project; don't remove existing packages
RUN uv sync --inexact --locked --no-dev

# Run without heartbeat, mingle, gossip to reduce network overhead
# https://stackoverflow.com/questions/66961952/how-can-i-scale-down-celery-worker-network-overhead
CMD ["sh", "-c", "celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO"]
