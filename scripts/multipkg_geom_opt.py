"""This scripts shows to easy it is to seamlessly interoperate four QC programs--
geometric, xtb, terachem, and psi4--to quickly achieve a computational outcome
such as a highly optimized geometry"""

from qcelemental.models import Molecule

from bigchem.tasks import compute_procedure

# Define the parameters for each program
input_specifications = [
    ("xtb", {"model": {"method": "GFN2-xTB"}}),
    ("terachem_fe", {"model": {"method": "b3lyp", "basis": "6-31g"}}),
    ("psi4", {"model": {"method": "CCSD(T)", "basis": "cc-PVQZ"}}),
]

molecule = Molecule.from_data("pubchem:water")

# Iteratively optimize the molecule using four different QC programs using the exact
# same standardized input/output objects
for program, input_spec in input_specifications:
    optimization_input = {
        "initial_molecule": molecule,
        "input_specification": input_spec,
        "keywords": {"program": program},
    }
    # Send inputs to BigChem and collect results
    result = compute_procedure.delay(optimization_input, "geometric").get()
    molecule = result.final_molecule
