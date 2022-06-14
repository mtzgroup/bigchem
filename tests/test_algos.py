import pytest
from qcelemental.models.results import AtomicInput, AtomicResult

from bigqc.algos import parallel_frequency_analysis, parallel_hessian
from bigqc.canvas import group


# NOTE: Not checking aggressively for correctness. Check that with test_hessian_task,
# may want to improve in future.
@pytest.mark.skip("Long test")
@pytest.mark.parametrize(
    "driver,model,engine,batch",
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
def test_parallel_hessian(water, driver, model, engine, batch):
    atomic_input = AtomicInput(
        molecule=water,
        driver=driver,
        model=model,
    )
    sig = parallel_hessian(atomic_input, engine)
    if batch:
        sig = group([sig] * 2)

    future_result = sig.delay()
    result = future_result.get()
    # Submit Job
    if not batch:
        result = [result]
    for r in result:
        assert isinstance(r, AtomicResult)


@pytest.mark.skip("Long test")
@pytest.mark.parametrize(
    "driver,model,engine,kwargs,batch",
    (
        (
            "properties",
            {"method": "HF", "basis": "sto-3g"},
            "psi4",
            {
                "energy": 1.5,
                "temperature": 310,
                "pressure": 1.2,
            },
            False,
        ),
    ),
)
@pytest.mark.timeout(450)
def test_parallel_frequency_analysis(water, driver, model, engine, kwargs, batch):
    atomic_input = AtomicInput(
        molecule=water,
        driver=driver,
        model=model,
    )
    sig = parallel_frequency_analysis(atomic_input, engine, **kwargs)
    if batch:
        sig = group([sig] * 2)

    future_result = sig.delay()
    result = future_result.get()
    # Submit Job
    if not batch:
        result = [result]
    for r in result:
        assert isinstance(r, AtomicResult)
