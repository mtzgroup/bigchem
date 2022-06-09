import numpy as np
from qcelemental.models import AtomicResult
from qcelemental.util.serialization import json_loads

from bigqc.tasks import frequency_analysis, hessian


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
