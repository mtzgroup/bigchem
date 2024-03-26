from qcio import Molecule, ProgramInput

from bigchem.algos import parallel_frequency_analysis

# Create the molecule
# Can also open a molecule from a file
# molecule = Molecule.open("path/to/h2o.xyz")
molecule = Molecule(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0, 0.0, 0.0],
        [0.52421003, 1.68733646, 0.48074633],
        [1.14668581, -0.45032174, -1.35474466],
    ],
)

# Create ProgramInput
my_input = ProgramInput(
    molecule=molecule, model={"method": "b3lyp", "basis": "6-31g"}, calctype="hessian"
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
