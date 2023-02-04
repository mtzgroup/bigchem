import numpy as np
import pytest
from qcelemental.models import (
    AtomicInput,
    AtomicResult,
    FailedOperation,
    OptimizationInput,
    OptimizationResult,
)
from qcelemental.util.serialization import json_loads

from bigchem.canvas import group  # type:ignore
from bigchem.tasks import (
    compute,
    compute_procedure,
    frequency_analysis,
    hessian,
    result_to_input,
)


def test_hessian_task(test_data_dir, water):
    """Ensure that my hessian implementation matches previous result from Umberto"""

    with open(test_data_dir / "hessian_gradients.json") as f:
        gradients = [AtomicResult(**g) for g in json_loads(f.read())]

    # Testing task in foreground since no QC package is required
    # 5.03e-3 was the dh used to create these gradients
    result = hessian(gradients, 5.0e-3)

    answer = AtomicResult.parse_file(test_data_dir / "hessian_answer.json")
    np.testing.assert_almost_equal(
        result.return_result, answer.return_result, decimal=5
    )
    assert result.driver == "hessian"


def test_frequency_analysis_task(test_data_dir):
    hessian_ar = AtomicResult.parse_file(test_data_dir / "hessian_answer.json")
    result = frequency_analysis(hessian_ar)

    answer = AtomicResult.parse_file(test_data_dir / "frequency_analysis_answer.json")

    np.testing.assert_almost_equal(
        result.return_result["freqs_wavenumber"],
        answer.return_result["freqs_wavenumber"],
        decimal=0,
    )
    np.testing.assert_almost_equal(
        result.return_result["normal_modes_cart"],
        answer.return_result["normal_modes_cart"],
        decimal=0,
    )
    np.testing.assert_almost_equal(
        result.return_result["g_total_au"],
        answer.return_result["g_total_au"],
        decimal=2,
    )


def test_frequency_analysis_task_kwargs(test_data_dir):
    hessian_ar = AtomicResult.parse_file(test_data_dir / "hessian_answer.json")
    answer = AtomicResult.parse_file(test_data_dir / "frequency_analysis_answer.json")

    result = frequency_analysis(hessian_ar, energy=1.5, temperature=310, pressure=1.2)

    np.testing.assert_almost_equal(
        result.return_result["freqs_wavenumber"],
        answer.return_result["freqs_wavenumber"],
        decimal=0,
    )
    np.testing.assert_almost_equal(
        result.return_result["normal_modes_cart"],
        answer.return_result["normal_modes_cart"],
        decimal=0,
    )
    np.testing.assert_almost_equal(
        result.return_result["g_total_au"],
        1.5024387753853545,  # Different number from answer computed with no kwargs
        decimal=2,
    )


@pytest.mark.parametrize(
    "program,model,keywords,batch",
    (
        ("psi4", {"method": "HF", "basis": "sto-3g"}, {}, False),
        ("rdkit", {"method": "UFF"}, {}, False),
        ("xtb", {"method": "GFN2-xTB"}, {"accuracy": 1.0, "max_iterations": 20}, False),
        ("xtb", {"method": "GFN2-xTB"}, {"accuracy": 1.0, "max_iterations": 20}, True),
    ),
)
@pytest.mark.timeout(65)
def test_compute(hydrogen, program, model, keywords, batch):
    """Testings as one function so we don't submit excess compute jobs.

    NOTE: Timeout is long because the worker instance may be waiting to connect to
    RabbitMQ if it just started up. Celery's exponential back off means that
    it's possible a few early misses on worker -> MQ connection results in the
    worker waiting up for 8 seconds (or longer) to retry connecting.
    """
    atomic_input = AtomicInput(
        molecule=hydrogen, driver="energy", model=model, keywords=keywords
    )
    sig = compute.s(atomic_input, program)
    if batch:
        # Make list of inputs
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
        assert isinstance(r, AtomicResult)


@pytest.mark.parametrize(
    "optimizer,model,keywords,batch",
    (
        (
            "berny",
            {"method": "HF", "basis": "sto-3g"},
            {"program": "psi4", "maxsteps": 2},
            False,
        ),
        (
            "geometric",
            {"method": "HF", "basis": "sto-3g"},
            {"program": "psi4", "maxiter": 2},
            False,
        ),
        ("geometric", {"method": "UFF"}, {"program": "rdkit", "maxiter": 2}, False),
        ("geometric", {"method": "UFF"}, {"program": "rdkit", "maxiter": 2}, True),
    ),
)
@pytest.mark.timeout(65)
def test_compute_procedure_optimization(
    hydrogen,
    optimizer,
    keywords,
    model,
    batch,
):
    """See note in test_compute re: timeout"""
    optimization_input = OptimizationInput(
        input_specification={"driver": "gradient", "model": model},
        protocols={"trajectory": "all"},
        initial_molecule=hydrogen,
        keywords=keywords,
    )

    sig = compute_procedure.s(optimization_input, optimizer)
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
        assert isinstance(r, OptimizationResult)


def test_result_to_input_atomic_result(water):
    result = AtomicResult(
        molecule=water,
        driver="energy",
        provenance={"creator": "fake"},
        success=True,
        properties={},
        model={"method": "b3lyp", "basis": "6-31g"},
        return_result=-76.38506640227922,
    )
    # Not yet implemented. Remove this test once implemented
    with pytest.raises(NotImplementedError):
        result_to_input(result)


def test_result_to_input_failed_operation(water):
    fo = FailedOperation(
        input_data="fake",
        success=False,
        error={"error_type": "issue", "error_message": "something went wrong"},
    )
    # Not yet implemented. Remove this test once implemented
    with pytest.raises(ValueError):
        result_to_input(fo)


def test_result_to_input_optimization_result(water):
    opt_result = OptimizationResult(
        input_specification={"model": {"method": "b3lyp", "basis": "6-31g"}},
        initial_molecule=water,
        provenance={"creator": "fake"},
        final_molecule=water,
        trajectory=[],
        success=True,
        energies=[1, 2, 3],
    )

    new_spec = {
        "keywords": {"program": "new_prog"},
        "input_specification": {
            "model": {"method": "new_methods", "basis": "new_basis"}
        },
        "extras": {"ex1": "ex1"},
    }
    new_input = result_to_input(opt_result, **new_spec)
    assert (
        new_input.input_specification.model.dict()
        == new_spec["input_specification"]["model"]
    )

    assert new_input.keywords == new_spec["keywords"]
    assert new_input.extras == new_spec["extras"]
