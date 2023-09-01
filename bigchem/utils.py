"""Helper functions not for end users"""
from typing import List

import numpy as np
from qcio import CalcType, ProgramInput

from .config import settings


def _gradient_inputs(
    prog_input: ProgramInput, dh: float = settings.bigchem_default_hessian_dh
) -> List[ProgramInput]:
    """Create ProgramInput gradient calculations for a numerical hessian

    Params:
        prog_input: ProgramInput with keywords specific to the gradient computations
            that will comprise the hessian
        dh: Displacement for finite difference

    Returns:
        Flat list of ProgramInput gradient calculations with dh offset for each geometry
            value. The first ProgramInput represents a "forward" step by dh and the next
            ProgramInput represents a "backward" step by dh and so on.
    """
    as_dict = prog_input.model_dump()
    as_dict["calctype"] = CalcType.gradient
    grad_input = ProgramInput(**as_dict)

    gradients = []
    geometry = np.array(prog_input.molecule.geometry)
    # Get all indices in the 2D array as a list of pairs
    indices = np.indices(geometry.shape).reshape(2, -1).T

    for index in indices:
        # Need two new objects
        forward, backward = grad_input.model_copy(deep=True), grad_input.model_copy(
            deep=True
        )

        forward.molecule.geometry[tuple(index)] += dh
        backward.molecule.geometry[tuple(index)] -= dh

        gradients.append(forward)
        gradients.append(backward)

    return gradients
