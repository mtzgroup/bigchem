from itertools import zip_longest
from typing import List, Union

import numpy as np
from qcio import (
    CalcType,
    DualProgramInput,
    InputBase,
    OptimizationOutput,
    OutputBase,
    ProgramFailure,
    ProgramInput,
    QCProgramArgs,
    SinglePointOutput,
    SubProgramArgs,
)
from qcop import compute as qcop_compute

from .app import bigchem

__all__ = [
    "compute",
    "output_to_input",
    "assemble_hessian",
    "frequency_analysis",
]


@bigchem.task
def compute(
    program: Union[str, InputBase],
    inp_obj: Union[InputBase, str],
    raise_exc: bool = True,
    **kwargs,
) -> OutputBase:
    """Wrapper around qcop.compute.

    Checks first and second argument order as they may be reversed due to chaining.
    For example, output_to_input returns an output object, but compute expects program
    as the first argument. Chains can only pass the output object as the first argument
    to the next task in the chain. This wrapper allows the user to pass the program
    first or second.

    Raise exception by default so that celery knows when tasks fail. This is important
    for chaining tasks together. If a task fails, the chain will stop executing and
    the AsyncResult object will have a .failed() method that returns True.
    """
    if isinstance(inp_obj, str):
        # If the first argument is a string, then the second argument is the input
        program, inp_obj = inp_obj, program
    return qcop_compute(program, inp_obj, raise_exc=raise_exc, **kwargs)


@bigchem.task
def output_to_input(
    output: Union[SinglePointOutput, ProgramFailure, OptimizationOutput],
    calctype: CalcType,
    program_args: Union[QCProgramArgs, SubProgramArgs],
) -> Union[ProgramInput, DualProgramInput]:
    """Propagate output values from a calculation onto a new input object.

    Args:
        output: SinglePointOutput, OptimizationOutput, or ProgramFailure object
        program_args: QCProgramArgs or SubProgramArgs object
        calctype: Calculation type for the new input

    NOTE: This task requires additional work to cover more general cases. This skeleton
        is primarily to give an initial example of basic multi-package geometry
        optimization.
    """
    if isinstance(output, ProgramFailure):
        raise ValueError(
            "Previous operation failed and cannot be converted to a new input."
        )

    input_model = (
        ProgramInput if isinstance(program_args, QCProgramArgs) else DualProgramInput
    )
    if isinstance(output, OptimizationOutput):
        # Take final geometry from optimization and pass to next input
        return input_model(
            molecule=output.results.final_molecule,
            calctype=calctype,
            **program_args.model_dump(),
        )
    else:
        # TODO: Add wavefunction passing for TeraChem somewhere? Not here...
        raise NotImplementedError(
            f"No implementation for transforming {output.__class__.__name__} objects "
            f"into {input_model.__name__} objects yet."
        )


@bigchem.task
def assemble_hessian(
    gradients: List[SinglePointOutput], dh: float
) -> Union[SinglePointOutput, ProgramFailure]:
    """Assemble hessian from an array of gradient computations

    Params:
        gradients: List of gradient AtomicResult objects alternating between a
            "forward" and "backward" computation. NOTE: The last computation on the
            list is a basic energy calculation of the original geometry.
        dh: The displacement used for finite difference displacements of gradient
            geometries

    Note:
        Another way I've tested this algorithm is to compute the hessian using psi4
        and then using this algorithm at the save level of theory and then compare
        their eigenvalues. The results have always matched up to two decimal places.
        The matrices can't be compared directly because it appears psi4 does some sort
        of rotation on their matrix, so the eigenvalues are a better mechanism for
        comparison.
    """
    # Validate input array; return FailedOperation if a gradient or energy failed
    for gradient in gradients:
        if isinstance(gradient, ProgramFailure):
            return gradient

    # Pop energy calculation of original geometry from gradients (last value in
    # gradients list)
    energy_output = gradients.pop()

    dim = len(gradients[0].input_data.molecule.symbols) * 3
    hessian = np.zeros((dim, dim), dtype=float)

    for i, (forward, backward) in enumerate(zip_longest(*[iter(gradients)] * 2)):
        val = (forward.return_result - backward.return_result) / (dh * 2)
        hessian[i] = val.flatten()

    output = energy_output.model_dump()
    output["input_data"]["calctype"] = CalcType.hessian
    output["results"]["hessian"] = hessian

    return SinglePointOutput(**output)


@bigchem.task
def frequency_analysis(
    sp_output: SinglePointOutput, **kwargs
) -> Union[SinglePointOutput, ProgramFailure]:
    """Adds geomeTRIC's frequency analysis results to hessian SinglePointOutput

    Params:
        sp_output: SinglePointOutput with .results.hessian value
        kwargs: Keywords passed to geomeTRIC's frequency_analysis function
            temperature: float - Temperature passed to the harmonic free energy module;
                default: 300.0
            pressure: float - Pressure passed to the harmonic free energy module;
                default: 1.0

    Returns:
        SinglePointOutput with additional results:
            freqs_wavenumber: List of vibrational frequencies in wavenumbers
            normal_modes_cartesian: List of normal modes in cartesian coordinates
            gibbs_free_energy: Gibbs free energy in Hartree

    """
    # Import here so client applications don't need to install geomeTRIC
    from geometric.normal_modes import frequency_analysis as geometric_freqs_analysis

    freqs, n_modes, g_tot = geometric_freqs_analysis(
        sp_output.input_data.molecule.geometry.flatten(),  # numpy array
        sp_output.results.hessian,
        elem=sp_output.input_data.molecule.symbols,  # regular python list
        # Electronic energy passed to free energy module
        energy=sp_output.results.energy,
        **kwargs,
    )
    output = sp_output.model_dump()
    output["results"].update(
        {
            "freqs_wavenumber": freqs.tolist(),
            "normal_modes_cartesian": n_modes,
            "gibbs_free_energy": g_tot,
        }
    )
    return SinglePointOutput(**output)


@bigchem.task
def add(x, y):
    """Add two numbers

    NOTE: Used for design testing
    """
    return x + y


@bigchem.task
def task_sum(values: List[Union[float, int]], extra: int = 0) -> Union[float, int]:
    """Sum all the values in a list

    NOTE: Used for design testing as a summation at the end of add (a chord)
        e.g., async_result = group(add.s(i, i) for i in range(max)) | csum.s()
    """
    values.append(extra)
    return sum(values)
