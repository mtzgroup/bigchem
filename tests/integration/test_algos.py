import pytest
from numpy.testing import assert_allclose
from qcio import (
    CalcType,
    OptimizationOutput,
    ProgramInput,
    SinglePointOutput,
    SubProgramArgs,
)

from bigchem.algos import multistep_opt, parallel_frequency_analysis, parallel_hessian
from bigchem.tasks import compute


@pytest.mark.timeout(450)
def test_parallel_hessian(hydrogen):
    prog_input = ProgramInput(
        molecule=hydrogen,
        calctype="hessian",
        model={"method": "HF", "basis": "sto-3g"},
    )
    fr = parallel_hessian("psi4", prog_input).delay()
    output = fr.get()
    fr.forget()
    psi4_fr = compute.delay("psi4", prog_input)
    psi4_result = psi4_fr.get()
    psi4_fr.forget()

    assert isinstance(output, SinglePointOutput)
    assert_allclose(output.results.hessian, psi4_result.results.hessian, atol=1e-4)


@pytest.mark.timeout(450)
def test_parallel_frequency_analysis(water):
    # Must use water or some other non-linear molecule
    prog_input = ProgramInput(
        molecule=water,
        calctype="hessian",
        model={"method": "b3lyp", "basis": "6-31g"},
    )
    fr = parallel_frequency_analysis(
        "psi4", prog_input, temperature=310, pressure=1.2
    ).delay()
    output = fr.get()
    fr.forget()
    assert isinstance(output, SinglePointOutput)
    assert_allclose(
        [1619.135, 3615.209, 3780.138],
        output.results.freqs_wavenumber,
        atol=1e-1,
    )


@pytest.mark.timeout(65)
def test_multistep_opt(hydrogen):
    """See note in test_compute re: timeout"""
    # Define multi-package input_specs
    program_args = [
        SubProgramArgs(
            subprogram="xtb",
            subprogram_args={"model": {"method": "GFN2-xTB"}},
        ),
        SubProgramArgs(
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
