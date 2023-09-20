"""Top level functions for parallelized BigChem algorithms"""
from typing import List, Union

from qcio import (
    CalcType,
    DualProgramInput,
    Molecule,
    ProgramInput,
    QCProgramArgs,
    SubProgramArgs,
)

from .canvas import Signature, group
from .config import settings
from .tasks import assemble_hessian, compute, frequency_analysis, output_to_input
from .utils import _gradient_inputs


def parallel_hessian(
    program: str,
    prog_input: ProgramInput,
    dh: float = settings.bigchem_default_hessian_dh,
) -> Signature:
    """Create parallel hessian signature

    Params:
        program: Compute engine to use for gradient calculations
        prog_input: ProgramInput with driver=hessian
        dh: Displacement for finite difference computation

    Note: Creates a Celery Chord where gradients are computed in parallel, then the
        list of gradients is passed as the first argument to the hessian celery task.
        If called asynchronously, this function will return an AsyncResult with a
        .parent attribute referencing the group of gradient computations. The last
        computation in the gradient list is a basic energy calculation of the original
        geometry. It is used to create the final AtomicResult object for the hessian.
    """
    assert (
        prog_input.calctype == CalcType.hessian
    ), f"input_data.driver should be '{CalcType.hessian}', got '{prog_input.calctype}'"

    gradients = _gradient_inputs(prog_input, dh)
    # Perform basic energy computation on original molecule as final item in group
    energy_calc = prog_input.model_dump()
    energy_calc["calctype"] = "energy"
    gradients.append(ProgramInput(**energy_calc))

    # | is chain operator in celery
    return group(compute.s(program, p_inp) for p_inp in gradients) | assemble_hessian.s(
        dh
    )


def parallel_frequency_analysis(
    program: str,
    prog_input: ProgramInput,
    dh: float = settings.bigchem_default_hessian_dh,
    **kwargs,
) -> Signature:
    """Create frequency_analysis signature leveraging parallel hessian

    Params:
        program: Program to use for gradient calculations to generate hessian
        prog_input: ProgramInput object.
        dh: Displacement for finite difference computation of hessian
        kwargs: Keywords passed to geomeTRIC's frequency_analysis function
            temperature: float - Temperature passed to the harmonic free energy module;
                default: 300.0
            pressure: float - Pressure passed to the harmonic free energy module;
                default: 1.0

    """
    hessian_inp = prog_input.model_dump()
    # So parallel_hessian doesn't raise error
    hessian_inp["calctype"] = CalcType.hessian
    hessian_sig = parallel_hessian(program, ProgramInput(**hessian_inp), dh)
    # | is celery chain operator
    return hessian_sig | frequency_analysis.s(**kwargs)


def multistep_opt(
    molecule: Molecule,
    calctype: CalcType,
    programs: List[str],
    program_args: List[Union[QCProgramArgs, SubProgramArgs]],
    **kwargs,
) -> Signature:
    """Use multiple steps to sequentially optimize a molecule

    Params:
        program: The name of the program use for optimization
        prog_inputs: Program inputs for each optimization step.
        kwargs: All kwargs for qcop.compute() function
    """
    # Create first optimization in the chain
    if isinstance(program_args[0], QCProgramArgs):
        first_opt = ProgramInput(
            calctype=calctype, molecule=molecule, **program_args[0].model_dump()
        )
    else:
        first_opt = DualProgramInput(
            calctype=calctype, molecule=molecule, **program_args[0].model_dump()
        )
    task_chain = compute.s(programs[0], first_opt, **kwargs)

    # Add subsequent optimizations to the chain
    for program, prog_args in zip(programs[1:], program_args[1:]):
        task_chain = (
            task_chain
            | output_to_input.s(calctype, prog_args)
            | compute.s(program, **kwargs)
        )
    return task_chain
