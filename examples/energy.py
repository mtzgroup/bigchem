"""How to perform a basic, one-task calculation using BigChem"""

import qcengine as qcng
from qcelemental.models import AtomicInput

from bigchem.tasks import compute

# Instantiate Molecule
water = qcng.get_molecule("water")

# Create AtomicInput
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="energy"
)

# Submit computation to BigChem
future_result = compute.delay(my_input, "psi4")

# Check status (optional)
print(future_result.status)

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
