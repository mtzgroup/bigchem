from qcio import ProgramInput, Structure

from bigchem.algos import parallel_frequency_analysis

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

# Create ProgramInput
my_input = ProgramInput(
    structure=structure,
    calctype="hessian",  # type: ignore
    model={"method": "b3lyp", "basis": "6-31g"},  # type: ignore
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
