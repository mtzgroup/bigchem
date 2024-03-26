#!/bin/bash
#SBATCH --job-name=bigchem_worker
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2 # Adjust based on your requirements
#SBATCH --mem=8G          # Adjust based on your requirements
#SBATCH --array=1-10      # Number of BigChem workers; Adjust based on your requirements
#SBATCH --output=/path/to/logs/%x_%A_%a.out # %x is the job name, %A is job ID, %a is array task ID # Adjust or omit based on your requirements

# Load any QC packages you want BigChem to use (use the appropriate loading command for your system)
module load psi4/1.9.1 # Example; adjust based on your requirements
module load terachem   # Example; adjust based on your requirements

# Set environment variables - replace these placeholders with actual values
export BIGCHEM_BROKER_URL="amqp://your_broker_url_or_ip_here"
# Example: export BIGCHEM_BROKER_URL="amqp://173.77.23.33"
# Example: export BIGCHEM_BROKER_URL="amqp://rabbitmq.mydomain.com"
export BIGCHEM_BACKEND_URL="redis://your_backend_url_or_ip_here/0"
# Example: export BIGCHEM_BACKEND_URL="redis://173.77.23.33/0"
# Example: export BIGCHEM_BACKEND_URL="redis://redis.mydomain.com/0"
export BIGCHEM_VERSION="" # Set if desired, if blank latest will be used

# Load Python module, or use conda; BigChem supports Python 3.8+
module load python3 # Use appropriate command for your system

# Create and source a virtual environment (or use conda)
python3 -m venv bigchem_env # Only need to create it once
source bigchem_env/bin/activate
# Alternative: conda activate bigchem

# Install specific version of bigchem
pip install -U "bigchem${BIGCHEM_VERSION:+==$BIGCHEM_VERSION}[qcengine]"

# Start the Celery worker
celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO