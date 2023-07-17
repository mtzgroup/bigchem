import pytest
from qcio import (
    CalcType,
    DualProgramArgs,
    OptimizationOutput,
    ProgramInput,
    SinglePointOutput,
)

from bigchem.algos import multistep_opt, parallel_frequency_analysis, parallel_hessian
from bigchem.canvas import group


# NOTE: Not checking aggressively for correctness. Check that with test_hessian_task,
# may want to improve in future.
@pytest.mark.integration
@pytest.mark.parametrize(
    "calctype,model,program,batch",
    (
        (
            "hessian",
            {"method": "HF", "basis": "sto-3g"},
            "psi4",
            False,
        ),
        (
            "hessian",
            {"method": "HF", "basis": "sto-3g"},
            "psi4",
            True,
        ),
    ),
)
@pytest.mark.timeout(450)
def test_parallel_hessian(hydrogen, calctype, model, program, batch):
    prog_input = ProgramInput(
        molecule=hydrogen,
        calctype=calctype,
        model=model,
    )
    sig = parallel_hessian(program, prog_input)
    if batch:
        sig = group([sig] * 2)

    future_result = sig.delay()
    result = future_result.get()
    # Submit Job
    if not batch:
        result = [result]
    for r in result:
        assert isinstance(r, SinglePointOutput)


@pytest.mark.integration
@pytest.mark.parametrize(
    "calctype,model,program,kwargs,batch",
    (
        (
            "energy",
            {"method": "HF", "basis": "sto-3g"},
            "psi4",
            {
                "temperature": 310,
                "pressure": 1.2,
            },
            False,
        ),
    ),
)
@pytest.mark.timeout(450)
def test_parallel_frequency_analysis(water, calctype, model, program, kwargs, batch):
    # Must use water or some other non-linear molecule
    prog_input = ProgramInput(
        molecule=water,
        calctype=calctype,
        model=model,
    )
    sig = parallel_frequency_analysis(program, prog_input, **kwargs)
    if batch:
        sig = group([sig] * 2)

    future_result = sig.delay()
    result = future_result.get()
    # Submit Job
    if not batch:
        result = [result]
    for r in result:
        assert isinstance(r, SinglePointOutput)


@pytest.mark.timeout(65)
def test_multistep_opt(hydrogen):
    """See note in test_compute re: timeout"""
    # Define multi-package input_specs
    program_args = [
        DualProgramArgs(
            subprogram="xtb",
            subprogram_args={"model": {"method": "GFN2-xTB"}},
        ),
        DualProgramArgs(
            subprogram="psi4",
            subprogram_args={"model": {"method": "b3lyp", "basis": "sto-3g"}},
        ),
    ]
    # Submit job
    future_result = multistep_opt(
        hydrogen, CalcType.optimization, ["geometric", "geometric"], program_args
    )()
    result = future_result.get()

    # Assertions
    assert future_result.ready() is True
    assert isinstance(result, OptimizationOutput)

    # Check that the final optimization is performed with the last input_spec
    assert result.input_data.subprogram == program_args[-1].subprogram
    assert (
        result.input_data.subprogram_args.model
        == program_args[-1].subprogram_args.model
    )
