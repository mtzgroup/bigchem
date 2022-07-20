"""Quick example of how to perform a group of energy calculations"""

from qcelemental.models import AtomicInput, Molecule

from bigchem.canvas import group
from bigchem.tasks import compute

water = Molecule.from_data("pubchem:water")
atomic_input = AtomicInput(
    molecule=water,
    model={"method": "B3LYP", "basis": "6-31g"},
    driver="energy",
    # keywords={"bad": "fake"},
)

fr = group([compute.s(atomic_input, "psi4"), compute.s(atomic_input, "psi4")])()

print(fr.successful())
print(fr.ready())
print(fr.waiting())
print(fr.completed_count())
result = fr.get()
print(result)
