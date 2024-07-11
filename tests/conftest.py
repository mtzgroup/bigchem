from pathlib import Path

import numpy as np
import pytest
from qcio import ProgramInput, ProgramOutput, Structure


@pytest.fixture
def hydrogen():
    """Hydrogen Structure"""
    return Structure(
        symbols=["H", "H"],
        geometry=[[0.0, 0.0, -0.65], [0.0, 0.0, 0.65]],
        connectivity=[[0, 1, 1]],
    )


@pytest.fixture
def water():
    """Water Structure"""
    return Structure(
        symbols=["O", "H", "H"],
        # Optimized using geomeTRIC and psi4
        geometry=[
            [0.02379257, 0.0176149, -0.0124449],
            [0.50166098, 1.71746166, 0.51974588],
            [1.14656841, -0.49722813, -1.38188835],
        ],
        connectivity=[[0, 1, 1], [0, 2, 1]],
    )


@pytest.fixture(scope="function")
def prog_inp(hydrogen):
    """Create a function that returns a ProgramInput object with a specified
    calculation type."""

    def create_prog_input(calctype):
        return ProgramInput(
            structure=hydrogen,
            calctype=calctype,
            # Integration tests depend up this model; do not change
            model={"method": "hf", "basis": "sto-3g"},
            # Tests depend upon these keywords; do not change
            keywords={
                "purify": "no",
                "some-bool": False,
            },
        )

    return create_prog_input


@pytest.fixture
def prog_output(prog_inp):
    """Create ProgramOutput object"""
    sp_inp_energy = prog_inp("energy")
    energy = 1.0
    n_atoms = len(sp_inp_energy.structure.symbols)
    gradient = np.arange(n_atoms * 3).reshape(n_atoms, 3)
    hessian = np.arange(n_atoms**2 * 3**2).reshape(n_atoms * 3, n_atoms * 3)

    return ProgramOutput(
        input_data=sp_inp_energy,
        stdout="program standard out...",
        success=True,
        results={
            "energy": energy,
            "gradient": gradient,
            "hessian": hessian,
        },
        provenance={"program": "qcio-test-suite", "scratch_dir": "/tmp/qcio"},
        extras={"some_extra": 1},
    )


@pytest.fixture
def test_data_dir():
    """Test data directory Path"""
    return Path(__file__).parent / "test_data"
