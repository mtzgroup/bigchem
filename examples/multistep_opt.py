"""This scripts shows to easy it is to seamlessly interoperate four QC programs--
geometric, xtb, TeraChem, and psi4--to quickly achieve a computational outcome
such as a highly optimized geometry while distributing work across all available
worker instances simultaneously on multiple structures at once."""

from qcio import CalcType, ProgramArgsSub, Structure

from bigchem import group, multistep_opt

# Create the structures
# Can also open a structure from a file
# structure = Structure.open("path/to/h2o.xyz")
structures = [
    Structure(
        symbols=["O", "H", "H"],
        geometry=[  # type: ignore
            [0.0, 0.0, 0.0],
            [0.52421003, 1.68733646, 0.48074633],
            [1.14668581, -0.45032174, -1.35474466],
        ],
    ),
    Structure(
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
# Define the program for each optimization step
programs = ["geometric", "geometric", "geometric"]

# Define the parameters for each program
program_args = [
    ProgramArgsSub(
        subprogram="xtb",
        subprogram_args={"model": {"method": "GFN2xTB"}},  # type: ignore
    ),
    ProgramArgsSub(
        subprogram="terachem",
        subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},  # type: ignore # noqa: E501
    ),
    ProgramArgsSub(
        subprogram="psi4",
        subprogram_args={"model": {"method": "CCSD(T)", "basis": "cc-PVQZ"}},  # type: ignore # noqa: E501
    ),
]

# Create a group of chains (each chain is one sequence of multi-step optimizations).
future_result = group(
    multistep_opt(structure, CalcType.optimization, programs, program_args)  # type: ignore # noqa: E501
    for structure in structures
).delay()
results = future_result.get()
future_result.forget()
