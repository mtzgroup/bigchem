from time import sleep

import qcengine as qcng
from celery.states import UNREADY_STATES
from qcelemental.models import AtomicInput

from bigqc.tasks import compute

print(
    "Be sure to run 'docker-compose up -d' from the root directory before running this"
    " script!\n"
)
water = qcng.get_molecule("water")
my_input = AtomicInput(
    molecule=water, model={"method": "b3lyp", "basis": "6-31g"}, driver="energy"
)

print("Submitting computation to backend.")
async_result = compute.delay(my_input, "psi4")
# async_result = qc_compute.delay(my_input, "psi4")
print("Submitted!")
# Check status
while async_result.status in UNREADY_STATES:
    print(f"Computation status: {async_result.status}")
    sleep(0.2)
# Block until result is ready
result = async_result.get()
async_result.forget()
print(f"Computation Result: {result}")
