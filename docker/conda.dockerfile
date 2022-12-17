# Dockerfile for BigChem Worker. Contains BigChem code and CPU-only QC Packages
# Follows https://stackoverflow.com/a/54763270/5728276
FROM continuumio/miniconda3:4.10.3

LABEL maintainer="Colton Hicks <colton@coltonhicks.com>"

# https://github.com/awslabs/amazon-sagemaker-examples/issues/319
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.1 \
    # Install to system python, no need for venv
    POETRY_VIRTUALENVS_CREATE=false \
    # To run celery as root with pickle serializer; OK since in container
    C_FORCE_ROOT=true

# Install System Packages
RUN apt-get update && \
    # for psutil in qcengine
    # https://github.com/giampaolo/psutil/blob/master/INSTALL.rst
    apt-get install -y gcc python3-dev && \
    python -m pip install --upgrade pip && \ 
    python -m pip install "poetry==$POETRY_VERSION"

# Install QC Packages and BigChem
WORKDIR /code/
COPY pyproject.toml poetry.lock docker/env.yaml ./
RUN conda env update -f env.yaml && \
    conda clean -afy
RUN poetry install --no-dev --no-interaction --no-ansi
# RUN python -m pip install -r worker.requirements.txt

# Copy in code
COPY bigchem/ bigchem/

# Run without heartbeat, mingle, gossip to reduce network overhead
# https://stackoverflow.com/questions/66961952/how-can-i-scale-down-celery-worker-network-overhead
CMD ["sh", "-c", "celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO"]
