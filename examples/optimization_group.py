"""How to perform an optimization using BigChem"""

from qcio import CalcType, DualProgramInput, Molecule

from bigchem import compute, group

# Create the molecules
# Can also open a molecule from a file
# molecule = Molecule.open("path/to/h2o.xyz")
molecules = [
    Molecule(
        symbols=["O", "H", "H"],
        geometry=[  # type: ignore
            [0.0, 0.0, 0.0],
            [0.52421003, 1.68733646, 0.48074633],
            [1.14668581, -0.45032174, -1.35474466],
        ],
    ),
    Molecule(
        symbols=["C", "C", "H", "H", "H", "H", "H", "H"],
        geometry=[  # type: ignore
            [1.54034068e00, -1.01730824e00, 9.31281020e-01],
            [4.07197633e00, -9.75682600e-02, -2.20357900e-02],
            [2.56360000e-04, 1.39534000e-03, 1.11212000e-03],
            [1.30983131e00, -3.03614919e00, 5.49185670e-01],
            [1.38003941e00, -7.18125650e-01, 2.97078784e00],
            [5.61209917e00, -1.11612499e00, 9.07991580e-01],
            [4.30241880e00, 1.92102239e00, 3.60573450e-01],
            [4.23222331e00, -3.96191600e-01, -2.06158818e00],
        ],
    ),
]

# Define program inputs
prog_inputs = [
    DualProgramInput(
        molecule=molecule,
        calctype=CalcType.optimization,
        subprogram="psi4",
        subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},  # type: ignore # noqa: E501
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
