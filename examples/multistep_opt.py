"""This scripts shows to easy it is to seamlessly interoperate four QC programs--
geometric, xtb, TeraChem, and psi4--to quickly achieve a computational outcome
such as a highly optimized geometry while distributing work across all available
worker instances simultaneously on multiple molecules at once."""

from pathlib import Path

from qcio import CalcType, Molecule, SubProgramArgs

from bigchem import group, multistep_opt

current_dir = Path(__file__).resolve().parent

# Create the molecules
molecules = [
    Molecule.open(current_dir / "h2o.xyz"),
    Molecule.open(current_dir / "ethane.xyz"),
]
# Define the program for each optimization step
programs = ["geometric", "geometric", "geometric"]

# Define the parameters for each program
program_args = [
    SubProgramArgs(
        subprogram="xtb",
        subprogram_args={"model": {"method": "GFN2-xTB"}},
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
