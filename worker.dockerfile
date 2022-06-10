# Dockerfile for BigQC Worker. Contains BigQC code and CPU-only QC Packages
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
    POETRY_VERSION=1.1.13 \
    # Install to system python, no need for venv
    POETRY_VIRTUALENVS_CREATE=false

# Install QC packages
# https://github.com/giampaolo/psutil/blob/master/INSTALL.rst
RUN conda install psi4=1.6 -c psi4 && \
    # msgpack-python is for psi4
    conda install msgpack-python && \ 
    conda install -c conda-forge rdkit=2020.09.5 && \
    conda install -c conda-forge xtb-python=20.2 && \
    apt-get update && \
    # Need gcc and python3-dev for python psutil package (used by qcengine)
    apt-get install -y gcc python3-dev && \
    pip install "poetry==$POETRY_VERSION"


# Install dependencies
WORKDIR /code/
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy in code
COPY bigqc/ bigqc/

# Run without heartbeat, mingle, gossip to reduce network overhead
# https://stackoverflow.com/questions/66961952/how-can-i-scale-down-celery-worker-network-overhead
CMD ["sh", "-c", "celery -A bigqc.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO"]
