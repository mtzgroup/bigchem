from qcelemental.models.results import AtomicInput

from bigqc.helpers import _gradient_inputs


def test_gradient_inputs(water):
    dh = 1

    gradients = _gradient_inputs(
        AtomicInput(molecule=water, model={"method": "fake"}, driver="hessian"), dh
    )

    assert len(gradients) == (3 * 2 * len(water.symbols))

    geoms = []
    for i in range(len(water.geometry.flatten())):
        for sign in [1, -1]:
            modified_geom = water.geometry.flatten()
            modified_geom[i] += dh * sign
            geoms.append(modified_geom)

    for i, geom in enumerate(geoms):
        assert gradients[i].driver == "gradient"
        assert (gradients[i].molecule.geometry.flatten() == geom).all()
