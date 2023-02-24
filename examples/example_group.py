from celery.canvas import group
from qcelemental.models import AtomicInput, Molecule

from bigchem.tasks import compute

print(
    "Be sure to run 'docker compose up -d --build' from the root directory before running this"
    " script!\n"
)
water = Molecule.from_data("pubchem:water")
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="energy"
)
print("Submitting...")
group_sig = group(
    compute.s(my_input, "psi4", local_options={"ncores": 1}) for _ in range(3)
)

group_result = group_sig.delay()
print("Submitted!")

# Block until result is ready
print("Computing...")
result = group_result.get()

# Delete result from the backend
group_result.forget()
print(f"Computation Result: {result}")
