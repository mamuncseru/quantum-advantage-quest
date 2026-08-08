"""Tests for DQI's mechanism and for the baseline it has to beat.

Three carry the page: `test_the_spectrum_lives_on_low_weight_codewords` is
the reduction from optimisation to coding theory, verified rather than
re-derived; `test_the_semicircle_is_the_large_m_limit` checks the paper's
central law against an exact eigenvalue; and
`test_structure_reaches_further_than_randomness` is the 2026 lesson with a
mechanism attached.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from dqi_spectrum import (best_objective, best_over_all_radii,
                          objective_sign, optimal_weights,
                          polynomial_of_objective, random_instance,
                          reachable_frequencies, satisfied_count,
                          satisfied_fraction, semicircle_convergence,
                          semicircle_prediction, semicircle_regime,
                          spectrum_support, tridiagonal_form, walsh)
from prange_baseline import (advantage_window, dqi_fraction,
                             prange_finite_size_bonus, prange_fraction,
                             prange_prediction, prange_best, prange_once,
                             reed_solomon_radius, required_radius, solve_gf2)


# ============================================ the reduction to a code =====

def test_the_objective_is_fourier_sparse():
    """s(x) = sum_i (-1)^(b_i + a_i.x) has its whole spectrum on the m
    constraint vectors — which is why a code appears at all."""
    rng = np.random.default_rng(1)
    n, m = 9, 5
    A, b = random_instance(n, m, rng)
    sup = spectrum_support(objective_sign(A, b, n))
    assert sup <= set(A) | {0}
    assert len(sup) <= m


@pytest.mark.parametrize("ell", [1, 2, 3, 4])
def test_the_spectrum_lives_on_low_weight_codewords(ell):
    """THE reduction: a degree-ell polynomial of the objective has all its
    Fourier weight on XOR-combinations of at most ell constraint vectors.
    Verified by direct transform, not by re-deriving the algebra."""
    rng = np.random.default_rng(2)
    n, m = 10, 6
    A, b = random_instance(n, m, rng)
    s = objective_sign(A, b, n)
    P = polynomial_of_objective(s, [0] * ell + [1])       # s^ell
    assert spectrum_support(P) <= reachable_frequencies(A, ell)


def test_higher_degree_reaches_strictly_further():
    rng = np.random.default_rng(3)
    A, b = random_instance(10, 6, rng)
    sizes = [len(reachable_frequencies(A, l)) for l in (1, 2, 3)]
    assert sizes[0] < sizes[1] < sizes[2]


def test_walsh_is_an_involution_up_to_normalisation():
    rng = np.random.default_rng(4)
    v = rng.normal(size=64)
    assert np.abs(walsh(walsh(v)) - v).max() < 1e-10


def test_objective_sign_matches_the_count():
    rng = np.random.default_rng(5)
    n, m = 8, 7
    A, b = random_instance(n, m, rng)
    s = objective_sign(A, b, n)
    for x in (0, 3, 11, 200):
        assert s[x] == pytest.approx(2 * satisfied_count(A, b, x) - m)


# ================================================ the semicircle ==========

def test_the_form_is_tridiagonal_with_the_stated_couplings():
    T = tridiagonal_form(20, 5)
    assert T.shape == (6, 6)
    for k in range(5):
        assert T[k, k + 1] == pytest.approx(np.sqrt((k + 1) * (20 - k)))
    assert np.abs(np.diag(T)).max() == 0.0


def test_more_radius_is_never_worse_inside_the_regime():
    m = 200
    fr = [satisfied_fraction(m, l) for l in (5, 20, 50, 100)]
    assert fr == sorted(fr)


def test_the_semicircle_is_the_large_m_limit():
    """The paper's law, checked against an exact eigenvalue: the gap has to
    *shrink with m*, which is the only honest way to verify an asymptotic."""
    rows = semicircle_convergence(ms=(50, 100, 400, 1600), d=0.25)
    gaps = [abs(ex - sc) for _, ex, sc in rows]
    assert gaps == sorted(gaps, reverse=True)
    assert gaps[-1] < 0.01


@pytest.mark.parametrize("d", [0.1, 0.25, 0.4])
def test_the_law_holds_at_several_densities(d):
    m = 1200
    ell = int(round(d * m))
    assert satisfied_fraction(m, ell) == pytest.approx(
        semicircle_prediction(d), abs=0.02)


def test_the_peak_sits_at_half_the_constraints():
    frac, best_l = best_over_all_radii(400)
    assert best_l == semicircle_regime(400)
    assert frac == pytest.approx(1.0, abs=0.01)


def test_the_model_is_only_trusted_below_half():
    """Past d = 1/2 the tridiagonal reduction leaves its regime and its
    eigenvalue drifts toward m, which would claim DQI solves the problem
    exactly. Pinned so nobody quotes that number."""
    m = 200
    assert satisfied_fraction(m, int(0.95 * m)) > 0.99
    assert semicircle_prediction(0.95) < 0.73        # the law disagrees
    assert semicircle_regime(m) == 100


def test_the_weights_are_not_uniform():
    w = optimal_weights(200, 20)
    assert w.shape == (21,)
    assert np.abs(np.linalg.norm(w) - 1) < 1e-9
    assert w.max() > 3 * abs(w[0])


# ================================================ the baseline ============

def test_gf2_solver_solves():
    rng = np.random.default_rng(6)
    n = 8
    A, b = random_instance(n, n, rng)
    x = solve_gf2(A, b, n)
    if x is not None:
        for a, bb in zip(A, b):
            assert (bin(a & x).count("1") & 1) == bb


def test_prange_satisfies_its_information_set_exactly():
    """One draw solves n constraints exactly, so the count can never be
    below n — a floor the formula is built on."""
    rng = np.random.default_rng(7)
    n, m = 8, 40
    A, b = random_instance(n, m, rng)
    got = prange_once(A, b, n, rng)
    if got is not None:
        assert got >= n


def test_prange_matches_its_formula_up_to_a_finite_size_bonus():
    for n, m in ((8, 32), (10, 80)):
        meas = prange_fraction(n, m, trials=6, tries=25, seed=2)
        pred = prange_prediction(n, m)
        assert pred <= meas <= pred + 0.2


def test_the_finite_size_bonus_shrinks_with_m():
    """Repeating Prange helps, and the help vanishes as the instance grows —
    otherwise the asymptotic line would be the wrong baseline."""
    rows = prange_finite_size_bonus(ms=(32, 128, 256), trials=5, tries=25)
    assert rows[-1][3] < rows[0][3]
    assert rows[-1][3] < 0.07


def test_repeating_prange_never_hurts():
    rng = np.random.default_rng(8)
    A, b = random_instance(10, 60, rng)
    few = prange_best(A, b, 10, np.random.default_rng(9), tries=3)
    many = prange_best(A, b, 10, np.random.default_rng(9), tries=60)
    assert many >= few


# ================================================ the head-to-head ========

@pytest.mark.parametrize("n,m", [(10, 100), (40, 100), (80, 100)])
def test_a_radius_exists_that_beats_prange(n, m):
    ell = required_radius(n, m)
    assert ell is not None
    assert dqi_fraction(m, ell) > prange_prediction(n, m)
    assert dqi_fraction(m, ell - 1) <= prange_prediction(n, m)


def test_harder_baselines_demand_bigger_radii():
    """The specification handed to coding theory: as the classical attacker
    gets stronger, the decoder DQI needs gets deeper."""
    radii = [required_radius(n, 100) for n in (10, 20, 40, 60, 80)]
    assert all(r is not None for r in radii)
    assert radii == sorted(radii)


def test_structure_reaches_further_than_randomness():
    """The 2026 lesson, with a mechanism: Reed-Solomon has an efficient
    decoder reaching a constant fraction of m; a random code has none beyond
    information-set decoding, which is the attacker's own algorithm — so on
    random instances DQI would be asking Prange to beat Prange."""
    m = 200
    for k in (20, 50, 100):
        assert reed_solomon_radius(m, k) > 0.25 * m
    assert reed_solomon_radius(m, 20) > reed_solomon_radius(m, 100)
    assert reed_solomon_radius(m, 50, list_decoding=True) > \
        reed_solomon_radius(m, 50, list_decoding=False)


def test_reed_solomon_radius_beats_what_prange_needs():
    """Concretely: at m = 200 against an n = 50 attacker, list decoding
    reaches further than the radius required — which is why OPI is the
    instance family still standing."""
    m, n = 200, 50
    need = required_radius(n, m)
    assert need is not None
    assert reed_solomon_radius(m, 50) > need
