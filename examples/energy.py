"""How to perform a basic, single program calculation using BigChem"""
from pathlib import Path

from qcio import CalcType, Molecule, ProgramInput
from qcop.exceptions import QCOPBaseError

from bigchem import compute

current_dir = Path(__file__).resolve().parent

# Create the molecule
h2o = Molecule.open(current_dir / "h2o.xyz")

# Define the program input
prog_input = ProgramInput(
    molecule=h2o,
    calctype=CalcType.energy,
    model={"method": "b3lyp", "basis": "6-31gg"},
    # keywords={"purify": "no"},
)

# Submit computation to BigChem
try:
    future_output = compute.delay("terachem", prog_input)
    output = future_output.get()
except QCOPBaseError as e:
    exc = e
    # print(f"Program failure: {e.program_failure}")
    # print(f"Returncode: {e.returncode}")
    import pdb

    pdb.set_trace()
    exit(1)

# Check status (optional)
print(f"Calculation Status: {future_output.status}")

# Get result from BigChem
output = future_output.get()


# Remove result from backend
future_output.forget()

### Accessing results ###
# Stdout from the program
print(output.stdout)  # or output.pstdout for short
# Input data used to generate the calculation
print(output.input_data)
# Provenance of generated calculation
print(output.provenance)

# Check results
if output.success:
    print("Energy:", output.results.energy)
    # The CalcType results will always be available at .return_result
    print("Energy:", output.return_result)

else:  # output.success is False
    print(output.traceback)  # See why the program failed; output.ptraceback for short

print(output)
