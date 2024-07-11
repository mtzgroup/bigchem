"""How to perform a basic, single program calculation using BigChem"""

from qcio import CalcType, ProgramInput, Structure

from bigchem import compute

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

# Define the program input
prog_input = ProgramInput(
    structure=structure,
    calctype=CalcType.energy,
    model={"method": "b3lyp", "basis": "6-31g"},  # type: ignore
    keywords={"purify": "no"},
)

# Submit computation to BigChem
future_output = compute.delay("terachem", prog_input, collect_files=True)

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


# See all output files
print(f"Returned files: {output.files.keys()}")

# Write the returned files to your local machine
output.save_files()
print("Check your directory for all of the files produced by TeraChem.")

# This command is not necessary. Sometime a reverse proxy holds open a connection.
# This closes it gracefully. If instead the following error is raised when the script
# exits it is not a problem:
# 'ImportError: sys.meta_path is None, Python is likely shutting down'
# It just means the redis client was holding open a connection and did not get a chance
# to close it before python exited.
# future_output.backend.client.connection_pool.disconnect()
