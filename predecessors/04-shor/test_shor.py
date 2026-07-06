import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from qsim import amplitudes, apply, zero_state, H
from shor import find_order, qft, shor_factor


def test_qft_matches_dense_dft():
    t = 4
    rng = np.random.default_rng(2)
    psi0 = rng.normal(size=(2,) * t) + 1j * rng.normal(size=(2,) * t)
    psi0 /= np.linalg.norm(psi0)
    got = amplitudes(qft(psi0, list(range(t))))
    N = 2 ** t
    F = np.array([[np.exp(2j * np.pi * x * y / N) for x in range(N)]
                  for y in range(N)]) / np.sqrt(N)
    assert np.allclose(got, F @ amplitudes(psi0))


def test_order_finding():
    assert find_order(7, 15, seed=5) == 4     # 7^4 = 2401 = 1 mod 15
    assert find_order(2, 15, seed=5) == 4
    assert find_order(2, 21, seed=5) == 6     # 2^6 = 64 = 1 mod 21


def test_factor_15_and_21():
    assert shor_factor(15, seed=1)[:2] == (3, 5)
    assert shor_factor(21, seed=1)[:2] == (3, 7)
