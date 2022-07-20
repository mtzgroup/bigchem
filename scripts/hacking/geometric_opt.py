"""Quick example of how to perform a geomeTRIC optimization"""
import qcengine as qcng
from qcelemental.models.procedures import (
    OptimizationInput,
    OptimizationProtocols,
    QCInputSpecification,
    TrajectoryProtocolEnum,
)

from bigchem.tasks import compute_procedure as cp_task

water = qcng.get_molecule("water")
op = OptimizationProtocols(trajectory=TrajectoryProtocolEnum.all)
input_spec = QCInputSpecification(
    driver="gradient",
    model={"method": "b3lyp", "basis": "6-31g"},
)

inp = OptimizationInput(
    protocols=op,
    initial_molecule=water,
    input_specification=input_spec,
    keywords={"program": "psi4"},
)

r = cp_task.delay(inp, "geometric")
r.status
# o may be OptimizationResult or FailedOperation
o = r.get()
print(o)
