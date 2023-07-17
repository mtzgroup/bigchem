from pathlib import Path

import numpy as np
import pytest
from qcio import Molecule, ProgramInput, SinglePointOutput


@pytest.fixture
def hydrogen():
    """Hydrogen Molecule"""
    return Molecule(
        symbols=["H", "H"],
        geometry=[[0.0, 0.0, -0.65], [0.0, 0.0, 0.65]],
        connectivity=[[0, 1, 1]],
    )


@pytest.fixture
def water():
    """Water Molecule"""
    return Molecule(
        symbols=["O", "H", "H"],
        geometry=[
            [0.000000000000, 0.000000000000, 0.000000000000],
            [0.277400001481, 0.892900001365, 0.254400001949],
            [0.606799998451, -0.238300002277, -0.716900000349],
        ],
        connectivity=[[0, 1, 1], [0, 2, 1]],
    )


@pytest.fixture(scope="function")
def prog_inp(hydrogen):
    """Create a function that returns a ProgramInput object with a specified
    calculation type."""

    def create_prog_input(calctype):
        return ProgramInput(
            molecule=hydrogen,
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
def sp_output(prog_inp):
    """Create SinglePointOutput object"""
    sp_inp_energy = prog_inp("energy")
    energy = 1.0
    n_atoms = len(sp_inp_energy.molecule.symbols)
    gradient = np.arange(n_atoms * 3).reshape(n_atoms, 3)
    hessian = np.arange(n_atoms**2 * 3**2).reshape(n_atoms * 3, n_atoms * 3)

    return SinglePointOutput(
        input_data=sp_inp_energy,
        stdout="program standard out...",
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
