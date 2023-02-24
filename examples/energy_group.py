"""How to submit a group of tasks to BigChem"""

import qcengine as qcng
from qcelemental.models import AtomicInput

from bigchem.canvas import group
from bigchem.tasks import compute

# Instantiate Molecules
molecules = [
    qcng.get_molecule("water"),
    qcng.get_molecule("ethane"),
    qcng.get_molecule("hydrogen"),
]


# Create Group of task Signatures
future_result = group(
    compute.s(
        AtomicInput(
            molecule=molecule,
            model={"method": "b3lyp", "basis": "6-31g"},
            driver="energy",
        ),
        "psi4",
    )
    for molecule in molecules
).delay()

# Check if group is ready (optional)
print(future_result.ready())

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
