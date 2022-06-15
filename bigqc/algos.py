"""Top level functions for parallelized BigQC algorithms"""

from celery.canvas import Signature, group
from qcelemental.models import AtomicInput, DriverEnum

from .config import settings
from .helpers import _gradient_inputs
from .tasks import compute as compute_task
from .tasks import frequency_analysis as frequency_analysis_task
from .tasks import hessian as hessian_task


def parallel_hessian(
    input_data: AtomicInput,
    engine: str,
    dh: float = settings.bigqc_default_hessian_dh,
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
    return group(compute_task.s(inp, engine) for inp in gradients) | hessian_task.s(dh)


def parallel_frequency_analysis(
    input_data: AtomicInput,
    engine: str,
    dh: float = settings.bigqc_default_hessian_dh,
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
    return hessian_sig | frequency_analysis_task.s(**kwargs)
