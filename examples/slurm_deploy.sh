#!/bin/bash
#SBATCH --job-name=bigchem_worker
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2  # Adjust based on your requirements
#SBATCH --mem=16G          # Adjust based on your requirements
#SBATCH --array=1-10       # Number of BigChem workers; Adjust based on your requirements
#SBATCH --output=%x_%A_%a-logs.out # %x is the job name, %A is job ID, %a is array task ID # Write logs for each worker; Adjust or omit based on your requirements

conda activate bigchem
module load xxx # Example; adjust based on your requirements
# Tell the worker where to find the broker and backend (redis server)
# Example: export BIGCHEM_BROKER_URL="redis://10.1.34.4/0
export BIGCHEM_BROKER_URL="redis://your_head_node_hostname_or_ip/0"
export BIGCHEM_BACKEND_URL="redis://your_head_node_hostname_or_ip/0"
# Start the worker
celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO