import qcengine as qcng
from qcelemental.models import AtomicInput

from bigchem.algos import parallel_frequency_analysis

# Instantiate Molecule
# NOTE: molecule is not an optimized geometry, so will have negative frequencies
water = qcng.get_molecule("water")

# Create AtomicInput
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="properties"
)

# Submit computation to BigChem
future_result = parallel_frequency_analysis(my_input, "psi4").delay()

# Check status (optional)
print(future_result.status)

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
