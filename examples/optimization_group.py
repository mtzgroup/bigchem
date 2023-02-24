import qcengine as qcng
from qcelemental.models import OptimizationInput

from bigchem.canvas import group
from bigchem.tasks import compute_procedure

# Instantiate Molecules
molecules = [
    qcng.get_molecule("water"),
    qcng.get_molecule("ethane"),
    qcng.get_molecule("hydrogen"),
]


# Create Group of task Signatures, submit to BigChem
future_result = group(
    compute_procedure.s(
        OptimizationInput(
            initial_molecule=molecule,
            input_specification={"model": {"method": "b3lyp", "basis": "6-31g"}},
            keywords={"program": "psi4"},
        ),
        "geometric",
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
