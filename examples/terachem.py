"""How to perform a basic, one-task calculation using BigChem"""

from pprint import pprint

import qcengine as qcng
from qcelemental.models import AtomicInput

from bigchem.tasks import compute

# Instantiate Molecule
water = qcng.get_molecule("water")

# Create AtomicInput
my_input = AtomicInput(
    molecule=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    driver="energy",
    keywords={"closed": True, "restricted": True, "purify": False},
    protocols={"native_files": "all"},  # Request all files from TeraChem Frontend
)

# Submit computation to BigChem
future_result = compute.delay(my_input, "terachem_fe")

# Check status (optional)
print(future_result.status)

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

# See stdout
pprint(result.stdout)

# See all natives files
print(f"Returned files: {result.native_files.keys()}")

# Write some returned files to local machine:
with open("c0", "wb") as f:  # "wb" for binary data
    f.write(result.native_files["c0"])

with open("geom.molden", "w") as f:  # "w" for text data
    f.write(result.native_files["geom.molden"])

with open("tc.out", "w") as f:  # "w" for text data
    f.write(result.stdout)

print(result)
print("Check your directory for a 'c0', 'geom.molden', and 'tc.out' file.")

# This command is not necessary. Sometime a reverse proxy holds open a connection.
# This closes it gracefully. If instead the following error is raised when the script
# exits it is not a problem:
# 'ImportError: sys.meta_path is None, Python is likely shutting down'
# It just means the redis client was holding open a connection and did not get a chance
# to close it before python exited.
future_result.backend.client.connection_pool.disconnect()
