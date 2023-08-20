"""How to perform an optimization using BigChem"""
from pathlib import Path

from qcio import CalcType, DualProgramInput, Molecule

from bigchem import compute, group

current_dir = Path(__file__).resolve().parent

# Create the molecules
molecules = [
    Molecule.open(current_dir / "h2o.xyz"),
    Molecule.open(current_dir / "ethane.xyz"),
]

# Define program inputs
prog_inputs = [
    DualProgramInput(
        molecule=molecule,
        calctype=CalcType.optimization,
        subprogram="psi4",
        subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
    )
    for molecule in molecules
]

# Create Group of task Signatures, submit to BigChem
future_output = group(
    compute.s("geometric", prog_input) for prog_input in prog_inputs
).delay()


# Check if group is ready (optional)
print(f"Computation Complete: {future_output.ready()}")

# Get result from BigChem; Will be list of output objects
outputs = future_output.get()

# Remove result from backend
future_output.forget()

### Accessing results ###
for output in outputs:
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
        # See why the program failed; output.ptraceback for short
        print(output.traceback)

print(outputs)
