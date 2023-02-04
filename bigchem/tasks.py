from itertools import zip_longest
from typing import List, Union

import numpy as np
import qcengine as qcng
from geometric.normal_modes import frequency_analysis as geometric_frequency_analysis
from qcelemental.models import (
    AtomicInput,
    AtomicResult,
    FailedOperation,
    OptimizationInput,
    OptimizationResult,
)

from .app import bigchem

compute = bigchem.task(qcng.compute)


compute_procedure = bigchem.task(qcng.compute_procedure)


@bigchem.task
def result_to_input(
    result: Union[AtomicResult, FailedOperation, OptimizationResult], **kwargs
) -> Union[AtomicInput, OptimizationResult]:
    """Convert a result object into an input object for a subsequent calculation.

    NOTE: This task requires additional work to cover more general cases. This skeleton
        is primarily to give an initial example of basic multi-package geometry
        optimization. The function can become more general purpose once QCSchema 2.0 is
        released.
    """
    if isinstance(result, FailedOperation):
        raise ValueError(
            "Previous operation failed and cannot be converted to a new input."
        )
    if isinstance(result, AtomicResult):
        # TODO: Add wavefunction passing for TeraChem
        raise NotImplementedError("No implementation for AtomicResult objects yet.")
    else:
        # isinstance(result, OptimizationResult):
        return OptimizationInput(initial_molecule=result.final_molecule, **kwargs)


@bigchem.task
def hessian(
    gradients: List[AtomicResult], dh: float
) -> Union[AtomicResult, FailedOperation]:
    """Compute hessian in parallel from array of gradient computations

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
        if isinstance(gradient, FailedOperation):
            return gradient

    # Pop energy calculation from gradients (last value in gradients list)
    energy = gradients.pop()

    dim = len(gradients[0].molecule.symbols) * 3
    hessian = np.zeros((dim, dim), dtype=float)

    for i, pair in enumerate(zip_longest(*[iter(gradients)] * 2)):
        forward, backward = pair
        val = (forward.return_result - backward.return_result) / (dh * 2)
        hessian[i] = val.flatten()

    result = energy.dict()
    result["driver"] = "hessian"
    result["return_result"] = hessian

    return AtomicResult(**result)


@bigchem.task
def frequency_analysis(
    input_data: AtomicResult, **kwargs
) -> Union[AtomicResult, FailedOperation]:
    """Perform geomeTRIC's frequency analysis using AtomicResult with hessian result

    Params:
        input_data: AtomicResult with return_result=hessian
        kwargs: Keywords passed to geomeTRIC's frequency_analysis function
            energy: float - Electronic energy passed to the harmonic free energy module
                default: 0.0
            temperature: float - Temperature passed to the harmonic free energy module;
                default: 300.0
            pressure: float - Pressure passed to the harmonic free energy module;
                default: 1.0

    Returns:
        AtomicResult | FailedOperation - AtomicResult will be driver=properties with
            dictionary of values returned from frequency_analysis as return_result

    """
    freqs, n_modes, g_tot_au = geometric_frequency_analysis(
        input_data.molecule.geometry.flatten(),
        input_data.return_result,
        list(input_data.molecule.symbols),
        **kwargs,
    )
    result = input_data.dict()
    result["driver"] = "properties"
    result["return_result"] = {
        "freqs_wavenumber": freqs.tolist(),
        "normal_modes_cart": n_modes.tolist(),
        "g_total_au": g_tot_au,
    }
    return AtomicResult(**result)


@bigchem.task
def add(x, y):
    """Add two numbers

    NOTE: Used for design testing
    """
    return x + y


@bigchem.task
def csum(values: List[Union[float, int]], extra: int = 0) -> Union[float, int]:
    """Sum all the values in a list

    NOTE: Used for design testing as a summation at the end of add (a chord)
        e.g., async_result = group(add.s(i, i) for i in range(max)) | csum.s()
    """
    values.append(extra)
    return sum(values)
