#!/usr/bin/env bash
set -euo pipefail

# Usage information.
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: bash install.sh [ENV_NAME]
This script creates a conda/mamba/micromamba environment and installs bigchem.
EOF
    exit 0
fi

# Determine the current shell type.
current_shell=$(basename "${SHELL:-bash}")

# Use the first script argument as the environment name.
ENV_NAME=${1:-bigchem}

# Check that curl is available.
if ! command -v curl &>/dev/null; then
    echo "Error: curl is required but not installed."
    exit 1
fi

# Allow URL override.
ENV_LOCK_URL="${ENV_LOCK_URL:-https://raw.githubusercontent.com/mtzgroup/bigchem/master/docker/env.lock}"

# Step 1: Ask the user to choose a package manager.
echo "Select package manager for environment creation:"
select pm in "conda" "mamba" "micromamba"; do
    if [[ -n "$pm" ]]; then
        # Verify that the selected package manager exists.
        if ! command -v "$pm" &>/dev/null; then
            echo "Error: ${pm} is not installed. Please install it first."
            exit 1
        fi
        echo "Using ${pm}."
        break
    else
        echo "Invalid selection. Please choose 1, 2, or 3."
    fi
done

# Determine environment root.
env_root=$("${pm}" info 2>/dev/null | grep "envs directories :" | head -n1 | awk '{print $4}')
if [[ -z "${env_root}" ]]; then
    echo "Error: Unable to determine the environment root for ${pm}."
    exit 1
fi
expected_path="${env_root}/${ENV_NAME}"

echo "Checking if the '${ENV_NAME}' environment exists for ${pm}..."
if "${pm}" env list 2>/dev/null | grep -qw "${expected_path}"; then
    echo "The '${ENV_NAME}' environment already exists for ${pm}."
    echo "Please remove it before proceeding by running:"
    echo "  ${pm} env remove -n ${ENV_NAME}"
    exit 1
fi

echo "Creating environment '${ENV_NAME}' using ${pm}..."

# Step 2 & 3: Download and use env.lock to create the environment.
if [ "$pm" == "conda" ]; then
    tmpfile=$(mktemp)
    trap 'rm -f "$tmpfile"' EXIT
    echo "Downloading env.lock to temporary file..."
    curl -L "$ENV_LOCK_URL" -o "$tmpfile"
    "$pm" create -n "${ENV_NAME}" -y --file "$tmpfile"
    # Temporary file will be removed by trap.
else
    "$pm" create -n "${ENV_NAME}" -y --file <(curl -L "$ENV_LOCK_URL")
fi

# Step 4: Activate the environment and install the package.
echo "Activating the '${ENV_NAME}' environment..."
if [ "$pm" == "micromamba" ]; then
    eval "$(${pm} shell hook --shell=bash)"
    "${pm}" activate "${ENV_NAME}"
else
    if command -v conda &>/dev/null; then
        CONDA_BASE=$(conda info --base)
        if [ -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]; then
            export PS1="${PS1:-}"
            source "${CONDA_BASE}/etc/profile.d/conda.sh"
        fi
    fi
    "${pm}" activate "${ENV_NAME}"
fi

echo "Installing bigchem[geometric] via pip..."
python -m pip install 'bigchem[geometric]'

echo "Installation complete!"

echo "To activate the '${ENV_NAME}' environment in a new session, run:"
if [ "$pm" == "micromamba" ]; then
    echo "  eval \"\$(${pm} shell hook --shell=${current_shell})\" && ${pm} activate ${ENV_NAME}"
else
    echo "  ${pm} activate ${ENV_NAME}"
fi
