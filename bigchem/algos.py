"""Top level functions for parallelized BigChem algorithms"""
from typing import Any, Dict, List

from celery.canvas import Signature, chain, group
from qcelemental.models import AtomicInput, DriverEnum, Molecule

from .config import settings
from .helpers import _gradient_inputs
from .tasks import (
    compute,
    compute_procedure,
    frequency_analysis,
    hessian,
    result_to_input,
)


def parallel_hessian(
    input_data: AtomicInput,
    engine: str,
    dh: float = settings.bigchem_default_hessian_dh,
) -> Signature:
    """Create parallel hessian signature

    Params:
        input_data: AtomicInput with driver=hessian
        engine: Compute engine to use for gradient calculations
        dh: Displacement for finite difference computation

    Note: Creates a Celery Chord where gradients are computed in parallel, then the
        list of gradients is passed as the first argument to the hessian celery task.
        If called asynchronously, this function will return an AsyncResult with a
        .parent attribute referencing the group of gradient computations. The last
        computation in the gradient list is a basic energy calculation of the original
        geometry. It is used to create the final AtomicResult object for the hessian.
    """
    assert (
        input_data.driver == DriverEnum.hessian
    ), f"input_data.driver should be '{DriverEnum.hessian}', got '{input_data.driver}'"

    gradients = _gradient_inputs(input_data, dh)
    # Perform basic energy computation on original molecule as final item in group
    energy_calc = input_data.dict()
    energy_calc["driver"] = "energy"
    gradients.append(AtomicInput(**energy_calc))

    # | is chain operator in celery
    return group(compute.s(inp, engine) for inp in gradients) | hessian.s(dh)


def parallel_frequency_analysis(
    input_data: AtomicInput,
    engine: str,
    dh: float = settings.bigchem_default_hessian_dh,
    **kwargs,
) -> Signature:
    """Create frequency_analysis signature leveraging parallel hessian

    Params:
        input_data: AtomicInput with driver=properties
        engine: Compute engine to use for gradient calculations to generate hessian
        dh: Displacement for finite difference computation of hessian
        kwargs: Keywords passed to geomeTRIC's frequency_analysis function
            energy: float - Electronic energy passed to the harmonic free energy module
                default: 0.0
            temperature: float - Temperature passed to the harmonic free energy module;
                default: 300.0
            pressure: float - Pressure passed to the harmonic free energy module;
                default: 1.0

    """
    assert input_data.driver == DriverEnum.properties, (
        f"input_data.driver should be '{DriverEnum.properties}', got "
        f"'{input_data.driver}'"
    )
    hessian_inp = input_data.dict()
    hessian_inp["driver"] = DriverEnum.hessian
    hessian_sig = parallel_hessian(AtomicInput(**hessian_inp), engine, dh)
    # | is celery chain operator
    return hessian_sig | frequency_analysis.s(**kwargs)


def multistep_opt(
    initial_molecule: Molecule,
    procedure: str,
    input_specs: List[Dict[str, Any]],
) -> Signature:
    """Use multiple QC packages to sequentially optimize a molecule

    Params:
        initial_molecule: The initial Molecule on which to begin an optimization
        procedure: The name of the procedure to run ("geometric" or "berny")
        input_specs: List of dicts containing the parameters for each optimization.
            Keys and values correspond to the arguments required to create an
            OptimizationInput object minus 'initial_molecule'. E.g.,
            {
                "keywords": {"program": "name_of_gradient_engine"},
                "input_specification": {"model": {"method": "b3lyp", "basis": "6-31g"}}
            }
    """
    # Create first optimization in the chain
    task_chain = chain(
        compute_procedure.s(
            {"initial_molecule": initial_molecule, **input_specs[0]}, procedure
        )
    )

    # Add subsequent optimizations to the chain
    for input_spec in input_specs[1:]:  # all input specs after the first
        task_chain = (
            task_chain
            | result_to_input.s(**input_spec)
            | compute_procedure.s(procedure)
        )
    return task_chain
