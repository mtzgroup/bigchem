"""This scripts shows to easy it is to seamlessly interoperate four QC programs--
geometric, xtb, TeraChem, and psi4--to quickly achieve a computational outcome
such as a highly optimized geometry while distributing work across all available
worker instances simultaneously on multiple molecules at once."""

from qcio import CalcType, Molecule, SubProgramArgs

from bigchem import group, multistep_opt

# Create the molecules
# Can also open a molecule from a file
# molecule = Molecule.open("path/to/h2o.xyz")
molecules = [
    Molecule(
        symbols=["O", "H", "H"],
        geometry=[
            [0.0, 0.0, 0.0],
            [0.52421003, 1.68733646, 0.48074633],
            [1.14668581, -0.45032174, -1.35474466],
        ],
    ),
    Molecule(
        symbols=["C", "C", "H", "H", "H", "H", "H", "H"],
        geometry=[
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
    SubProgramArgs(
        subprogram="xtb",
        subprogram_args={"model": {"method": "GFN2xTB"}},
    ),
    SubProgramArgs(
        subprogram="terachem",
        subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
    ),
    SubProgramArgs(
        subprogram="psi4",
        subprogram_args={"model": {"method": "CCSD(T)", "basis": "cc-PVQZ"}},
    ),
]

# Create a group of chains (each chain is one sequence of multi-step optimizations).
future_result = group(
    multistep_opt(molecule, CalcType.optimization, programs, program_args)
    for molecule in molecules
).delay()
results = future_result.get()
future_result.forget()
