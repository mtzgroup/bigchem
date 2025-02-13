#!/usr/bin/env bash
set -euo pipefail

# Determine the current shell type (e.g. "bash" or "zsh").
# If $SHELL is unset, default to "bash".
current_shell=$(basename "${SHELL:-bash}")

# Use the first script argument as the environment name.
ENV_NAME=${1:-bigchem}

# Check that curl is available.
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed."
    exit 1
fi

# Step 1: Ask the user to choose a package manager.
echo "Select package manager for environment creation:"
select pm in "conda" "mamba" "micromamba"; do
    if [[ -n "$pm" ]]; then
        echo "Using ${pm}."
        break
    else
        echo "Invalid selection. Please choose 1, 2, or 3."
    fi
done

# Check if the environment already exists.
env_root=$("${pm}" info 2>/dev/null | grep "envs directories :" | head -n1 | awk '{print $4}')
expected_path="${env_root}/${ENV_NAME}"

echo "Checking if the '${ENV_NAME}' environment exists for ${pm}..."
if ${pm} env list 2>/dev/null | grep -qw "$expected_path"; then
    echo "The '${ENV_NAME}' environment already exists for ${pm}."
    echo "Please remove it before proceeding by running:"
    echo "  ${pm} env remove -n ${ENV_NAME}"
    exit 1
fi

# URL of the env.lock file in the GitHub repo.
ENV_LOCK_URL="https://raw.githubusercontent.com/mtzgroup/bigchem/master/docker/env.lock"

echo "Creating environment '$ENV_NAME' using ${pm}..."

# Step 2 & 3: Download and use env.lock to create the environment.
if [ "$pm" == "conda" ]; then
    # conda may require a seekable file; use a temporary file.
    tmpfile=$(mktemp)
    echo "Downloading env.lock to temporary file..."
    curl -L "$ENV_LOCK_URL" -o "$tmpfile"
    ${pm} create -n $ENV_NAME -y --file "$tmpfile"
    rm "$tmpfile"
else
    # For mamba and micromamba, process substitution works fine.
    ${pm} create -n $ENV_NAME -y --file <(curl -L "$ENV_LOCK_URL")
fi

# Step 4: Activate the environment and install the package.
echo "Activating the '$ENV_NAME' environment..."
if [ "$pm" == "micromamba" ]; then
    eval "$(${pm} shell hook --shell=bash)"
    ${pm} activate $ENV_NAME
else
    # For conda/mamba, source conda.sh if available.
    if command -v conda &> /dev/null; then
        CONDA_BASE=$(conda info --base)
        if [ -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]; then
            # Ensure PS1 is set to avoid errors in non-interactive shells.
            export PS1="${PS1:-}"
            source "${CONDA_BASE}/etc/profile.d/conda.sh"
        fi
    fi
    ${pm} activate $ENV_NAME
fi

echo "Installing bigchem[geometric] via pip..."
python -m pip install 'bigchem[geometric]'

echo "Installation complete!"

# Final message: how to activate the environment in the future.
echo "To activate the '$ENV_NAME' environment in a new session, run:"
if [ "$pm" == "micromamba" ]; then
    echo "  eval \"\$(${pm} shell hook --shell=${current_shell})\" && ${pm} activate $ENV_NAME"
else
    echo "  ${pm} activate $ENV_NAME"
fi

