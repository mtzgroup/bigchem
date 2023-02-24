"""This scripts shows to easy it is to seamlessly interoperate four QC programs--
geometric, xtb, TeraChem, and psi4--to quickly achieve a computational outcome
such as a highly optimized geometry while distributing work across all available
worker instances simultaneously."""

from qcelemental.models import Molecule

from bigchem.algos import multistep_opt
from bigchem.canvas import group

# Define the molecules of interest
molecule_names = ["water", "caffeine", "aspirin", "benzene", "thf"]
molecules = [Molecule.from_data(f"pubchem:{name}") for name in molecule_names]

# Define the parameters for each program
input_specifications = [
    {
        "keywords": {"program": "xtb"},
        "input_specification": {"model": {"method": "GFN2-xTB"}},
    },
    {
        "keywords": {"program": "terachem_fe"},
        "input_specification": {"model": {"method": "b3lyp", "basis": "6-31g"}},
    },
    {
        "keywords": {"program": "psi4"},
        "input_specification": {"model": {"method": "CCSD(T)", "basis": "cc-PVQZ"}},
    },
]


# Create a group of chains (each chain is one sequence of multi-step optimizations).
future_result = group(
    multistep_opt(molecule, "geometric", input_specifications) for molecule in molecules
).delay()
result = future_result.get()
future_result.forget()
