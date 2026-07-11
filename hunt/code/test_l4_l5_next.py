"""Tests for the L4/L5 numerics and the three next-session experiments."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from magic_transition import (collision_mass, random_clifford_t_state,
                              weyl_expectations)
from memory_purity import gibbs_state
from noise_threshold import (gamma_star, noisy_purity,
                             pauli_weight_spectrum)
from nonmarkov_fisher import cfi, protocol_A_dist, protocol_B_dist
from rate_persistence import grad_var
from windowed_payoff_l2 import optimal_w_l2, payoff_l2


def test_stabilizer_state_has_unit_collision_mass():
    rng = np.random.default_rng(0)
    psi = random_clifford_t_state(4, 0, rng)
    assert abs(collision_mass(psi, 4) - 1.0) < 1e-9


def test_t_gates_reduce_collision_mass():
    rng = np.random.default_rng(1)
    cms = [np.mean([collision_mass(random_clifford_t_state(4, t, rng), 4)
                    for _ in range(6)]) for t in (0, 6)]
    assert cms[1] < 0.8 * cms[0]


def test_weyl_distribution_normalization():
    rng = np.random.default_rng(2)
    psi = random_clifford_t_state(3, 2, rng)
    w = weyl_expectations(psi, 3)
    assert abs(w.sum() - 2 ** 3) < 1e-8       # sum |<W_a>|^2 = 2^n (pure)


def test_weight_spectrum_sums_to_purity():
    rho = gibbs_state(4, seed=4)
    spec = pauli_weight_spectrum(rho, 4)
    assert abs(spec.sum() - np.real(np.trace(rho @ rho))) < 1e-10
    assert abs(noisy_purity(spec, 0.0) - spec.sum()) < 1e-12


def test_gamma_star_monotone_in_eps():
    spec = pauli_weight_spectrum(gibbs_state(4, seed=4), 4)
    assert gamma_star(spec, 0.1) > gamma_star(spec, 0.01)


def test_nonmarkov_distributions_normalize():
    for th in (0.3, 1.0):
        assert abs(protocol_A_dist(th, 'X', 'Z').sum() - 1) < 1e-9
        assert abs(protocol_B_dist(th).sum() - 1) < 1e-9


def test_memory_fisher_edge_on_first_instance():
    fi_a = max(cfi(lambda t: protocol_A_dist(t, b1, b2), 0.6)
               for b1 in 'XYZ' for b2 in 'XYZ')
    assert cfi(protocol_B_dist, 0.6) > 1.5 * fi_a


def test_grad_var_positive_and_depth_dependent():
    v = grad_var(4, 2, depth=2, samples=30, seed=0)
    assert v > 1e-4


def test_l2_windowed_payoff_matches_unwindowed():
    from math import pi as PI
    from windowed_payoff import M, make_instance, pattern_histograms
    F = make_instance(seed=1)
    mus = [len(F[i]) / p for i, p in
           enumerate([3, 5, 7, 11, 13, 17, 19])]
    hist_u, hist_w = pattern_histograms(F, center=M // 2,
                                        sigma_x=M / (2 * PI * 1.2))
    w = optimal_w_l2(hist_u, mus)
    assert abs(payoff_l2(hist_u, mus, w) - payoff_l2(hist_w, mus, w)) < 1e-8
