# Dockerfile for BigChem Worker. Contains BigChem code and QC programs.
# Follows https://stackoverflow.com/a/54763270/5728276

ARG BASE_IMAGE=mambaorg/micromamba:1.4-jammy
FROM $BASE_IMAGE

LABEL maintainer="Colton Hicks <colton@coltonhicks.com>"

# https://github.com/awslabs/amazon-sagemaker-examples/issues/319
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Install to system python, no need for venv
    POETRY_VIRTUALENVS_CREATE=false

# Perform root tasks
WORKDIR /opt/
USER root
RUN apt-get update && \
    # for psutil in qcengine
    # https://github.com/giampaolo/psutil/blob/master/INSTALL.rst
    apt-get install -y gcc python3-dev && \
    # So $MAMBA_USER can read/write to /opt/
    chown -R $MAMBA_USER /opt/
USER $MAMBA_USER

# Install QC Programs
COPY --chown=$MAMBA_USER:$MAMBA_USER docker/env.lock ./
RUN micromamba install -y -n base -f env.lock && \
    micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)

# Install BigChem dependencies
COPY --chown=$MAMBA_USER:$MAMBA_USER pyproject.toml poetry.lock ./
RUN python -m pip install --upgrade pip && \ 
    python -m pip install poetry && \
    poetry install --only main --all-extras --no-interaction --no-ansi

# Copy in code
COPY --chown=$MAMBA_USER:$MAMBA_USER bigchem/ bigchem/

# Run without heartbeat, mingle, gossip to reduce network overhead
# https://stackoverflow.com/questions/66961952/how-can-i-scale-down-celery-worker-network-overhead
CMD ["sh", "-c", "celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO"]
