import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from scipy.linalg import expm

from davies import (davies_superoperator, gibbs_state, heisenberg_with_fields,
                    site_op, spectral_gap)
from metropolis import exact_mean_energy, metropolis_mean_energy
from qsim import X, Y


def _setup(beta=1.0):
    n = 3
    H = heisenberg_with_fields(n)
    couplings = [site_op(X, i, n) for i in range(n)] + \
                [site_op(Y, i, n) for i in range(n)]
    return H, davies_superoperator(H, couplings, beta), gibbs_state(H, beta)


def test_gibbs_is_stationary():
    H, L, rho_beta = _setup()
    assert np.linalg.norm(L @ rho_beta.reshape(-1)) < 1e-8


def test_positive_gap_and_convergence():
    H, L, rho_beta = _setup()
    assert spectral_gap(L) > 0.01
    rho = np.eye(8, dtype=complex) / 8
    rho_t = (expm(L * 50.0) @ rho.reshape(-1)).reshape(8, 8)
    dist = 0.5 * np.abs(np.linalg.eigvalsh(rho_t - rho_beta)).sum()
    assert dist < 1e-4


def test_metropolis_matches_exact():
    n, beta = 10, 0.7
    exact = exact_mean_energy(n, beta)
    est = metropolis_mean_energy(n, beta, sweeps=5000, seed=3)
    assert abs(est - exact) < 0.15
