import qcengine as qcng
from qcelemental.models import OptimizationInput

from bigchem.tasks import compute_procedure

# Instantiate Molecules
molecule = qcng.get_molecule("water")


# Submit computation to BigChemI
future_result = compute_procedure.delay(
    OptimizationInput(
        initial_molecule=molecule,
        input_specification={"model": {"method": "b3lyp", "basis": "6-31g"}},
        keywords={"program": "psi4"},
    ),
    "geometric",
)

# Check if group is ready (optional)
print(future_result.ready())

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
