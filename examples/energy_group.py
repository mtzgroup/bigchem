"""How to submit a group of tasks to BigChem"""

from pathlib import Path

from qcio import CalcType, Molecule, ProgramInput

from bigchem import compute, group

current_dir = Path(__file__).resolve().parent

# Create the molecules
molecules = [
    Molecule.open(current_dir / "h2o.xyz"),
    Molecule.open(current_dir / "ethane.xyz"),
]

# Submit a group of computations to BigChem
future_output = group(
    compute.s(
        "psi4",
        ProgramInput(
            molecule=molecule,
            calctype=CalcType.energy,
            model={"method": "b3lyp", "basis": "6-31g"},
        ),
    )
    for molecule in molecules
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
        print("Energy:", output.results.energy)
        # The CalcType results will always be available at .return_result
        print("Energy:", output.return_result)

    else:  # output.success is False
        # See why the program failed; output.ptraceback for short
        print(output.traceback)

print(outputs)
