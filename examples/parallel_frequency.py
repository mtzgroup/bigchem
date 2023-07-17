from pathlib import Path

from qcio import Molecule, ProgramInput

from bigchem.algos import parallel_frequency_analysis

current_dir = Path(__file__).resolve().parent

# Create the molecule
h2o = Molecule.open(current_dir / "h2o.xyz")

# Create ProgramInput
my_input = ProgramInput(
    molecule=h2o, model={"method": "b3lyp", "basis": "6-31g"}, calctype="hessian"
)

# Submit computation to BigChem
future_result = parallel_frequency_analysis("psi4", my_input).delay()

# Check status (optional)
print(future_result.status)

# Get result from BigChem
result = future_result.get()

# Remove result from backend
future_result.forget()

print(result)
