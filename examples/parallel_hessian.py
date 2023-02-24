import qcengine as qcng
from qcelemental.models import AtomicInput

from bigchem.algos import parallel_hessian

# Instantiate Molecule
water = qcng.get_molecule("hydrogen")

# Create AtomicInput
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="hessian"
)

# Submit computation to BigChem
future_result = parallel_hessian(my_input, "psi4").delay()

# Check status (optional)
print(future_result.status)

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
