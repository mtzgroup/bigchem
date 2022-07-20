import numpy as np
from celery.result import AsyncResult
from qcelemental.models import AtomicInput, Molecule

from bigchem.algos import parallel_hessian
from bigchem.canvas import group

water = Molecule(
    symbols=["O", "H", "H"],
    geometry=[
        0.0,
        -0.1976080204,
        0.0,
        -1.4351100596000002,
        0.9269832487999999,
        0.0,
        1.4351100596000002,
        0.9269832487999999,
        0.0,
    ],
)

atomic_input = AtomicInput(
    molecule=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    driver="hessian",
)

# Umberto's Hessian computed at pbe0 and 3-21g level of theory
uh = np.array(
    [
        [
            6.77617084e-01,
            -1.76511606e-06,
            1.49786886e-07,
            -3.38808024e-01,
            2.74273170e-01,
            -1.45604437e-06,
            -3.38809037e-01,
            -2.74271587e-01,
            1.30625798e-06,
        ],
        [
            3.63655093e-06,
            4.23191793e-01,
            -4.29626935e-06,
            1.94249578e-01,
            -2.11594666e-01,
            2.43492153e-06,
            -1.94253194e-01,
            -2.11597318e-01,
            1.86134906e-06,
        ],
        [
            5.90109685e-07,
            4.24173517e-06,
            -1.87820002e-02,
            7.00880262e-07,
            -2.32953113e-06,
            9.39101110e-03,
            -1.34407152e-06,
            -2.04424359e-06,
            9.39098837e-03,
        ],
        [
            -3.38811111e-01,
            1.94270469e-01,
            2.41927399e-07,
            3.80199361e-01,
            -2.34272831e-01,
            5.44426123e-07,
            -4.13880321e-02,
            4.00022013e-02,
            -7.86353684e-07,
        ],
        [
            2.74258127e-01,
            -2.11595096e-01,
            3.26369361e-06,
            -2.34253159e-01,
            2.05869829e-01,
            -2.73113972e-06,
            -4.00051230e-02,
            5.72545361e-03,
            -5.32555860e-07,
        ],
        [
            -1.82809477e-06,
            -2.92696379e-06,
            9.38933582e-03,
            8.87032514e-07,
            1.39897496e-06,
            -1.15858091e-02,
            1.02907577e-06,
            1.42431119e-06,
            2.19647322e-03,
        ],
        [
            -3.38809024e-01,
            -1.94265169e-01,
            1.75715347e-06,
            -4.13884894e-02,
            -4.00048024e-02,
            -4.44225957e-07,
            3.80197483e-01,
            2.34269876e-01,
            -1.31292741e-06,
        ],
        [
            -2.74255758e-01,
            -2.11596261e-01,
            1.93666709e-06,
            4.00032406e-02,
            5.72696602e-03,
            -4.69691343e-07,
            2.34252599e-01,
            2.05869507e-01,
            -1.46697537e-06,
        ],
        [
            4.68759172e-07,
            9.67948877e-07,
            9.39089977e-03,
            5.88698068e-07,
            -1.05900425e-06,
            2.19590393e-03,
            -1.09073361e-06,
            1.67055700e-07,
            -1.15868036e-02,
        ],
    ]
)

p4hess = np.array(
    [
        [
            0.6704634479062104,
            0.0,
            0.0,
            -0.3352317239531058,
            0.0,
            0.262696695321551,
            -0.3352317239531058,
            0.0,
            -0.262696695321551,
        ],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [
            0.0,
            0.0,
            0.4148835473930372,
            0.1912255018433717,
            0.0,
            -0.2074417736965189,
            -0.1912255018433717,
            0.0,
            -0.2074417736965189,
        ],
        [
            -0.3352317239531058,
            0.0,
            0.1912255018433717,
            0.375131760228302,
            0.0,
            -0.2269610985824617,
            -0.0399000362751957,
            0.0,
            0.0357355967390898,
        ],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [
            0.2626966953215511,
            0.0,
            -0.2074417736965189,
            -0.2269610985824617,
            0.0,
            0.2066490240172189,
            -0.0357355967390898,
            0.0,
            0.0007927496793003,
        ],
        [
            -0.3352317239531058,
            0.0,
            -0.1912255018433717,
            -0.0399000362751957,
            0.0,
            -0.0357355967390898,
            0.375131760228302,
            0.0,
            0.2269610985824617,
        ],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [
            -0.2626966953215511,
            0.0,
            -0.2074417736965189,
            0.0357355967390898,
            0.0,
            0.0007927496793003,
            0.2269610985824617,
            0.0,
            0.2066490240172189,
        ],
    ]
)

hs = parallel_hessian(atomic_input, "psi4")
g = group([hs, hs])
fr = hs()
r = fr.get()
print(r)
frar = AsyncResult(fr.id)

# p4eg = np.sort(np.linalg.eig(p4hess)[0])
# tcceg = np.sort(np.linalg.eig(r.return_result)[0])

# # np.testing.assert_almost_equal(r.return_result, uh, decimal=5)
# np.testing.assert_almost_equal(p4eg, tcceg, decimal=2)

# NOTE: how to chain hessian to a frequency analysis calculation
# fa = (hs | frequency_analysis.s())()
# fr = fa.get()


# freq, disp, g_tot_au = frequency_analysis(atomic_input.molecule.geometry.flatten(), r.return_result, list(atomic_input.molecule.symbols))
