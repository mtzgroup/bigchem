from pathlib import Path

import pytest
import qcengine as qcng


@pytest.fixture
def water():
    """Water Molecule"""
    return qcng.get_molecule("water")


@pytest.fixture
def test_data_dir():
    """Test data directory Path"""
    return Path(__file__).parent / "test_data"
