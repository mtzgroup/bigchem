"""Quick example of how to perform a berny optimization"""

from os import environ

from qcelemental.models import Molecule
from qcelemental.models.procedures import (
    OptimizationInput,
    OptimizationProtocols,
    QCInputSpecification,
    TrajectoryProtocolEnum,
)

from bigchem.tasks import compute_procedure as cp_task

environ["TERACHEM_PBS_HOST"] = "127.0.0.1"
environ["TERACHEM_PBS_PORT"] = "11111"

water = Molecule.from_data("pubchem:water")
op = OptimizationProtocols(trajectory=TrajectoryProtocolEnum.all)
input_spec = QCInputSpecification(
    driver="gradient",
    model={"method": "b3lyp", "basis": "6-31g"},
)

inp = OptimizationInput(
    protocols=op,
    initial_molecule=water,
    input_specification=input_spec,
    keywords={"program": "psi4", "maxsteps": 3},
)

r = cp_task.delay(inp, "berny")
r.status
o = r.get()

print(o)
