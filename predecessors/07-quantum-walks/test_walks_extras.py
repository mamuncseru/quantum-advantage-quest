"""Tests for the transport mechanism, its fragility, and Szegedy's ceiling.

The two that matter most: `test_the_exponents_are_two_and_one` pins the one
number the whole speedup rests on, and
`test_disorder_turns_polynomial_decay_into_exponential` pins the critique —
the clean walk loses amplitude polynomially in depth, the disordered one
exponentially.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from glued_trees import quantum_exit_prob, reduced_adjacency
from szegedy import (barbell_chain, classical_hitting_scale, complete_chain,
                     cycle_chain, gap_ratio, is_reversible, lazy, path_chain,
                     phase_gap, predicted_phase_gap, quantum_hitting_scale,
                     spectral_gap, szegedy_walk)
from walk_transport import (classical_spread, clean_decay_exponent,
                            disorder_exponent, disordered_adjacency,
                            disordered_exit, exit_probability, fit_exponent,
                            localisation_length, max_depth_before_localisation,
                            participation_ratio, quantum_spread)


# =============================================== the mechanism =============

def test_the_exponents_are_two_and_one():
    """Ballistic versus diffusive, measured. Everything else in this autopsy
    is a consequence of these two numbers."""
    times = np.array([2, 4, 8, 16, 32, 64], dtype=float)
    L = 401
    assert fit_exponent(times, quantum_spread(L, times)) == pytest.approx(
        2.0, abs=0.02)
    assert fit_exponent(times, classical_spread(L, times)) == pytest.approx(
        1.0, abs=0.02)


def test_quantum_packet_stays_inside_its_light_cone():
    """Ballistic means a front, not a spread: essentially no amplitude
    beyond |x| ~ 2t (the group velocity of the path graph)."""
    L, t = 401, 30.0
    A = np.zeros((L, L))
    for j in range(L - 1):
        A[j, j + 1] = A[j + 1, j] = 1.0
    lam, V = np.linalg.eigh(A)
    start = np.zeros(L)
    start[L // 2] = 1.0
    psi = V @ (np.exp(-1j * lam * t) * (V.T @ start))
    p = np.abs(psi) ** 2
    xs = np.abs(np.arange(L) - L // 2)
    assert p[xs > 2.3 * t].sum() < 1e-3


def test_exit_probability_matches_the_existing_simulator():
    """`walk_transport.exit_probability` and `glued_trees.quantum_exit_prob`
    must be the same measurement."""
    for d in (8, 12, 16):
        a = exit_probability(reduced_adjacency(d), d=d)[0]
        b = quantum_exit_prob(d)[0]
        assert a == pytest.approx(b, abs=1e-12)


# ================================================ the fragility ============

def test_clean_decay_is_only_polynomial():
    """The clean walk does lose amplitude as the graph grows — the packet
    spreads — but at a harmless polynomial rate."""
    beta = clean_decay_exponent()
    assert 0.4 < beta < 0.8


@pytest.mark.parametrize("d", [16, 40])
def test_disorder_only_ever_hurts(d):
    ps = [disordered_exit(d, W, trials=8, seed=3)
          for W in (0.0, 0.5, 1.0, 2.0)]
    assert all(a >= b - 1e-9 for a, b in zip(ps, ps[1:]))


def test_disorder_turns_polynomial_decay_into_exponential():
    """The critique, in one assertion. Between d = 16 and d = 150 the clean
    walk loses a factor of ~4; at W = 2 it loses a factor of ~1000."""
    clean = [disordered_exit(d, 0.0, trials=4, seed=3) for d in (16, 150)]
    noisy = [disordered_exit(d, 2.0, trials=12, seed=3) for d in (16, 150)]
    assert clean[0] / clean[1] < 10
    assert noisy[0] / noisy[1] > 100


@pytest.mark.parametrize("W", [1.0, 2.0, 4.0])
def test_localisation_length_shrinks_with_disorder(W):
    xi_small = localisation_length(W, length=400, trials=3, seed=2)
    xi_smaller = localisation_length(2 * W, length=400, trials=3, seed=2)
    assert xi_smaller < xi_small


def test_localisation_follows_a_power_law():
    """xi ~ W^-alpha with alpha near 2 (the weak-disorder 1-D result);
    measured nearer 1.7 on finite chains, which the notes state rather than
    round away."""
    alpha = disorder_exponent(strengths=(1.0, 2.0, 4.0), length=400, trials=3)
    assert 1.3 < alpha < 2.2


def test_the_criterion_predicts_where_the_advantage_dies():
    """xi is measured on a *separate* long chain, so this is a prediction:
    once 2d+2 exceeds xi, the exit probability should have collapsed."""
    W = 2.0
    d_max = max_depth_before_localisation(W, length=400, trials=3, seed=2)
    assert 5 < d_max < 40
    inside = disordered_exit(int(d_max / 2), W, trials=12, seed=3)
    outside = disordered_exit(int(4 * d_max), W, trials=12, seed=3)
    assert outside < inside / 10


def test_participation_ratio_falls_with_disorder():
    rng = np.random.default_rng(0)
    clean = participation_ratio(disordered_adjacency(30, 0.0, rng))
    dirty = participation_ratio(disordered_adjacency(30, 4.0, rng))
    assert dirty < clean / 2


# =================================================== Szegedy ==============

CHAINS = [
    ("cycle", lazy(cycle_chain(10))),
    ("path", lazy(path_chain(10))),
    ("complete", lazy(complete_chain(8))),
    ("barbell", lazy(barbell_chain(5))),
]


@pytest.mark.parametrize("name,P", CHAINS)
def test_chains_are_reversible(name, P):
    """Szegedy's construction needs detailed balance; checked, not assumed."""
    assert is_reversible(P)


@pytest.mark.parametrize("name,P", CHAINS)
def test_walk_operator_is_unitary(name, P):
    W = szegedy_walk(P)
    assert np.abs(W.conj().T @ W - np.eye(W.shape[0])).max() < 1e-9


@pytest.mark.parametrize("name,P", CHAINS)
def test_phase_gap_is_arccos_of_the_classical_spectrum(name, P):
    """The theorem, measured on the operator we actually built."""
    assert phase_gap(szegedy_walk(P)) == pytest.approx(
        predicted_phase_gap(P), abs=1e-8)


def test_the_square_root_law_is_flat_across_chains():
    """phase gap / sqrt(spectral gap) is the same constant for chains whose
    gaps differ by more than an order of magnitude — so the square root is a
    law, not a coincidence of one example. The constant is 2*sqrt(2)."""
    ratios = [gap_ratio(P) for _, P in CHAINS
              if spectral_gap(P) < 0.3]          # away from the trivial end
    assert max(ratios) - min(ratios) < 0.05
    assert all(r == pytest.approx(2 * np.sqrt(2), abs=0.05) for r in ratios)


@pytest.mark.parametrize("name,P", CHAINS)
def test_the_speedup_is_exactly_quadratic(name, P):
    c, q = classical_hitting_scale(P), quantum_hitting_scale(P)
    assert c / q == pytest.approx(np.sqrt(c), rel=1e-9)


def test_a_fast_mixing_chain_has_nothing_to_speed_up():
    """The complete graph mixes in one step; its quantum walk saves almost
    nothing. Speedups live where the classical gap is small."""
    P = lazy(complete_chain(8))
    assert classical_hitting_scale(P) / quantum_hitting_scale(P) < 2.0
