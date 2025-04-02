"""These tests ensure that all the pipes are flowing correctly."""

import pytest
from qcio import CalcType, DualProgramInput, ProgramArgs, ProgramOutput

from bigchem.canvas import group  # type:ignore
from bigchem.tasks import compute


@pytest.mark.integration
@pytest.mark.parametrize(
    "optimizer,keywords,subprogram,model,batch",
    (
        # NO LONGER SUPPORTED
        # (
        #     "berny",
        #     {"method": "HF", "basis": "sto-3g"},
        #     {"program": "psi4", "maxsteps": 2},
        #     False,
        # ),
        (
            "geometric",
            {"maxiter": 10},
            "psi4",
            {"method": "HF", "basis": "sto-3g"},
            False,
        ),
        ("geometric", {"maxiter": 10}, "rdkit", {"method": "UFF"}, False),
        ("geometric", {"maxiter": 10}, "rdkit", {"method": "UFF"}, True),
    ),
)
@pytest.mark.timeout(65)
def test_compute_optimization(
    hydrogen,
    optimizer,
    keywords,
    subprogram,
    model,
    batch,
):
    """See note in test_compute re: timeout"""
    optimization_input = DualProgramInput(
        calctype=CalcType.optimization,
        structure=hydrogen,
        keywords=keywords,
        subprogram=subprogram,
        subprogram_args=ProgramArgs(
            model=model,
        ),
    )
    sig = compute.s(optimizer, optimization_input)
    if batch:
        sig = group([sig] * 2)

    # Submit Job
    future_result = sig.delay()
    result = future_result.get()

    # Assertions
    assert future_result.ready() is True

    # Check assertions about single results and groups
    if not isinstance(result, list):
        result = [result]
    for r in result:
        assert isinstance(r, ProgramOutput)
