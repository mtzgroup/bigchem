from celery.canvas import group
from qcelemental.models import AtomicInput, Molecule

from bigchem.tasks import compute

print(
    "Be sure to run 'docker-compose up -d' from the root directory before running this"
    " script!\n"
)
water = Molecule.from_data("pubchem:caffeine")
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="energy"
)
print("Submitting...")
group_sig = group(
    compute.s(my_input, "psi4", local_options={"ncores": 1}) for _ in range(10)
)

group_result = group_sig.delay()
print("Submitted!")
print("Computing...")
# Block until result is ready
result = group_result.get()

group_result.forget()
print(f"Computation Result: {result}")
