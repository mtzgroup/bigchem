"""How to perform an optimization using BigChem"""

from pathlib import Path

from qcio import CalcType, DualProgramInput, Molecule

from bigchem.tasks import compute

current_dir = Path(__file__).resolve().parent

# Create the molecule
h2o = Molecule.open(current_dir / "h2o.xyz")

# Define program input
prog_input = DualProgramInput(
    molecule=h2o,
    calctype=CalcType.optimization,
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
)

# Submit computation to BigChem
future_output = compute.delay(
    "geometric",
    prog_input,
)

# Check status (optional)
print(f"Calculation status: {future_output.status}")

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
    print("Energies:", output.results.energies)
    print("Molecules:", output.results.molecules)
    print("Trajectory:", output.results.trajectory)

else:  # output.success is False
    print(output.traceback)  # See why the program failed; output.ptraceback for short

print(output)
