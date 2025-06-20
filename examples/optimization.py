"""How to perform an optimization using BigChem"""

from qcio import CalcType, DualProgramInput, Structure
from qcop import exceptions

from bigchem.tasks import compute

# Create the structure
# Can also open a structure from a file
# structure = Structure.open("path/to/h2o.xyz")
structure = Structure(
    symbols=["O", "H", "H"],
    geometry=[  # type: ignore
        [0.0, 0.0, 0.0],
        [0.52421003, 1.68733646, 0.48074633],
        [1.14668581, -0.45032174, -1.35474466],
    ],
)

# Define program input
prog_input = DualProgramInput(
    structure=structure,
    calctype=CalcType.optimization,
    keywords={"maxiter": 25},  # Optional: Additional keywords to pass to geomeTRIC
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},  # type: ignore
)

# Submit computation to BigChem
future_output = compute.delay("geometric", prog_input)

# Check status (optional)
print(f"Calculation status: {future_output.status}")

try:
    # Get result from BigChem
    prog_output = future_output.get()

except exceptions.QCOPBaseError as e:
    prog_output = e.program_output

# Remove result from backend
future_output.forget()

### Accessing results ###
# Stdout from the program
print(prog_output.stdout)  # or prog_output.pstdout for short
# Input data used to generate the calculation
print(prog_output.input_data)
# Provenance of generated calculation
print(prog_output.provenance)

# Check results
if prog_output.success:
    print("Energies:", prog_output.results.energies)
    print("Structures:", prog_output.results.structures)
    print("Trajectory:", prog_output.results.trajectory)

else:  # prog_output.success is False
    # See why the program failed; prog_output.ptraceback for short
    print(prog_output.traceback)
