"""Invariant tests for the L6-L10 first numerics."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from certification_gap import gibbs_state_beta, marginal, weight_n_pauli
from ghz_shield import ghz_pair, marginal_without
from nonmarkov_fisher import cfi
from qualm_scaling import protocol_A_dist_T, protocol_B_dist_T
from ratio_telescope import factor_rel_var, spectrum
from symmetry_leakage import (dephased_state, local_hamiltonian,
                              max_low_weight_odd_y)


def test_ghz_marginals_identical_but_states_orthogonal():
    p, m = ghz_pair(6)
    assert abs(np.vdot(p, m)) < 1e-12
    for d in range(6):
        assert np.abs(marginal_without(p, 6, d)
                      - marginal_without(m, 6, d)).max() < 1e-12


def test_symmetry_leakage_dichotomy():
    Hr = local_hamiltonian(4, np.random.default_rng(0), False)
    Hc = local_hamiltonian(4, np.random.default_rng(0), True)
    assert max_low_weight_odd_y(dephased_state(Hr, 4), 4) < 1e-10
    assert max_low_weight_odd_y(dephased_state(Hc, 4), 4) > 0.02


def test_telescope_variance_shrinks_with_steps():
    w = spectrum(4, seed=1)
    single = factor_rel_var(w, 0.0, 2.0)
    halves = max(factor_rel_var(w, 0.0, 1.0), factor_rel_var(w, 1.0, 2.0))
    assert halves < single


def test_weight_n_pauli_has_zero_marginals():
    rho = gibbs_state_beta(4, 0.3, seed=4)
    W = weight_n_pauli(4)
    c = 0.5 * float(np.linalg.eigvalsh(rho).min())
    bad = rho + c * W
    assert np.abs(marginal(rho, 4, (0, 1)) - marginal(bad, 4, (0, 1))
                  ).max() < 1e-12
    assert 0.5 * np.abs(np.linalg.eigvalsh(bad - rho)).sum() > 1e-4


def test_qualm_distributions_and_growth():
    assert abs(protocol_A_dist_T(0.6, 'Z', 3).sum() - 1) < 1e-9
    assert abs(protocol_B_dist_T(0.6, 3).sum() - 1) < 1e-9
    fb2 = cfi(lambda t: protocol_B_dist_T(t, 2), 0.6)
    fb3 = cfi(lambda t: protocol_B_dist_T(t, 3), 0.6)
    assert fb3 > 1.5 * fb2          # temporal compounding
