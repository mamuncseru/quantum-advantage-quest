"""Tests for the phases and for the degrees.

The two that carry the page: `test_grovers_root_n_is_a_polynomial_degree` and
`test_simulation_degree_is_additive_in_precision` — together they are the
unification, stated as numbers rather than as a table of names.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from polynomial_cost import (best_approximation_error, chebyshev_basis,
                             degree_for_evolution, degree_for_gibbs,
                             degree_for_inverse, degree_for_sign, fit_scaling,
                             low_rank_imitability, low_rank_matrix, min_degree,
                             sparse_local_matrix, stable_rank)
from qsp_phases import (chebyshev, check_parity, conditioning_modulo_gauge,
                        fit_degree, gauge_dimension, phase_map_spectrum,
                        qsp_response, qsp_unitary, solve_phases)


# ================================================== the QSP construction ===

@pytest.mark.parametrize("d", [1, 2, 3, 5, 8])
def test_zero_phases_give_chebyshev(d):
    """QSP with every rotation set to the identity is the walk-operator demo:
    the response is exactly T_d. The two files describe the same object."""
    xs = np.linspace(-0.99, 0.99, 200)
    got = qsp_response(np.zeros(d + 1), xs)
    assert np.abs(got - chebyshev(d, xs)).max() < 1e-12


@pytest.mark.parametrize("d", [3, 7])
def test_batched_and_single_x_agree(d):
    """`qsp_response` is vectorised for speed; `qsp_unitary` is the readable
    one-x version. They must not drift apart."""
    rng = np.random.default_rng(d)
    ph = rng.uniform(-1, 1, d + 1)
    xs = np.linspace(-0.9, 0.9, 11)
    single = np.array([qsp_unitary(ph, float(x))[0, 0].real for x in xs])
    assert np.abs(qsp_response(ph, xs) - single).max() < 1e-12


@pytest.mark.parametrize("d", [2, 3, 4, 5, 6, 7])
def test_parity_is_forced_by_the_degree(d):
    """A degree-d QSP response always has parity d mod 2 — the constraint
    that decides which targets are reachable at all."""
    rng = np.random.default_rng(100 + d)
    for _ in range(3):
        assert check_parity(rng.uniform(-np.pi, np.pi, d + 1))


@pytest.mark.parametrize("d", [3, 4, 6])
def test_the_response_really_is_a_polynomial_of_that_degree(d):
    rng = np.random.default_rng(7 + d)
    info = fit_degree(rng.uniform(-1, 1, d + 1))
    assert info["residual"] < 1e-10
    assert info["highest"] == d


def test_the_response_is_bounded_by_one():
    """|P(x)| <= 1 for every reachable polynomial — it is a matrix entry of a
    unitary, so this is not an assumption but a consequence."""
    rng = np.random.default_rng(3)
    xs = np.linspace(-1, 1, 300)
    for d in (2, 5, 9):
        for _ in range(4):
            r = qsp_response(rng.uniform(-np.pi, np.pi, d + 1), xs)
            assert np.abs(r).max() <= 1.0 + 1e-12


@pytest.mark.parametrize("d", [2, 4, 6])
def test_phases_can_be_solved_for(d):
    _, resid = solve_phases(lambda x, d=d: chebyshev(d, np.array([x]))[0],
                            d, tries=1)
    assert resid < 1e-4


# ------------------------------------------- what is hard about phases -----

@pytest.mark.parametrize("d", [4, 8, 16, 32])
def test_the_phase_map_has_exactly_one_gauge_direction(d):
    """A real flat direction of the construction, present at every degree.
    Any phase-finding routine has to quotient it out."""
    assert gauge_dimension(d) == 1


def test_conditioning_modulo_gauge_grows_slowly():
    """Corrects a common impression: the phase map is NOT exponentially
    ill-conditioned. Between d = 4 and d = 32 — an eightfold rise in degree —
    the condition number grows by well under an order of magnitude, so what
    makes high-degree phase finding hard is the non-convex *search*, not the
    local geometry."""
    ds = [4, 8, 16, 32]
    conds = [conditioning_modulo_gauge(d) for d in ds]
    assert conds == sorted(conds)
    assert conds[-1] / conds[0] < 10
    assert fit_scaling(ds, conds) < 1.0          # sub-linear in d, not 2^d


def test_spectrum_has_the_right_size():
    for d in (4, 10):
        assert phase_map_spectrum(d).size == d + 1


# ============================================ algorithms as degrees ========

def test_grovers_root_n_is_a_polynomial_degree():
    """The headline. Approximating sign(x) outside a gap δ needs degree
    ∝ 1/δ, and with δ = 1/√N that is √N — Grover's query count, arrived at
    as the degree of a polynomial rather than as an iteration count."""
    deltas = [0.25, 0.125, 0.0625, 0.03125]
    degs = [degree_for_sign(d) for d in deltas]
    assert fit_scaling(deltas, degs) == pytest.approx(-1.0, abs=0.1)
    products = [d * delta for d, delta in zip(degs, deltas)]
    assert max(products) - min(products) < 0.5      # degree·δ is constant


def test_hhls_condition_number_is_a_polynomial_degree():
    kappas = [4, 8, 16, 32]
    degs = [degree_for_inverse(k) for k in kappas]
    assert fit_scaling(kappas, degs) == pytest.approx(1.0, abs=0.1)


def test_simulation_degree_is_linear_in_time_with_an_additive_offset():
    """degree = t + O(log 1/ε). Checked as an additive law, because fitting a
    power law to it reports a fake sublinear exponent."""
    ts = [8, 16, 32, 64, 128]
    degs = [degree_for_evolution(t) for t in ts]
    offsets = [d - t for d, t in zip(degs, ts)]
    assert all(0 < o < 40 for o in offsets)
    assert max(offsets) - min(offsets) < 15         # nearly constant
    assert fit_scaling(ts, degs) < 1.0              # the artefact, documented


def test_simulation_degree_is_additive_in_precision():
    """The exponential improvement in 1/ε, measured: tightening ε by four
    orders adds a handful of degrees to simulation while multiplying the
    other two."""
    eps = [1e-1, 1e-2, 1e-3, 1e-4]
    sim = [degree_for_evolution(8, e) for e in eps]
    sign = [degree_for_sign(0.125, e) for e in eps]
    inv = [degree_for_inverse(8, e) for e in eps]
    assert sim[-1] - sim[0] < 15                    # additive
    assert sign[-1] / sign[0] > 2.5                 # multiplicative
    assert inv[-1] / inv[0] > 2.5


def test_gibbs_degree_grows_with_inverse_temperature():
    degs = [degree_for_gibbs(b) for b in (1, 4, 16)]
    assert degs == sorted(degs)


def test_parity_costs_you_when_it_is_wrong():
    """A degree budget spent on the wrong parity buys nothing: an even basis
    cannot approximate an odd function at all."""
    xs = np.linspace(-1, 1, 400)
    odd_target = lambda x: x ** 3                                # noqa: E731
    good = best_approximation_error(odd_target, xs, 6, parity="odd")
    bad = best_approximation_error(odd_target, xs, 6, parity="even")
    assert good < 1e-10
    assert bad > 0.1


def test_min_degree_is_the_minimum():
    xs = np.linspace(-1, 1, 400)
    target = lambda x: np.cos(8 * x)                             # noqa: E731
    d = min_degree(target, xs, 1e-3, parity="even")
    assert best_approximation_error(target, xs, d, parity="even") <= 1e-3
    assert best_approximation_error(target, xs, d - 1, parity="even") > 1e-3


def test_chebyshev_basis_respects_parity():
    xs = np.linspace(-1, 1, 50)
    assert chebyshev_basis(6, xs, "even").shape[1] == 4      # k = 0,2,4,6
    assert chebyshev_basis(6, xs, "odd").shape[1] == 3       # k = 1,3,5


# ==================================== the other factor: the block-encoding =

def test_a_low_rank_encoding_is_imitable():
    """Tang's attack in one number: a rank-8 sketch reproduces a rank-8
    matrix exactly, so no polynomial degree can rescue the advantage."""
    A = low_rank_matrix(128, 8)
    assert low_rank_imitability(A, 8) < 1e-10


def test_a_sparse_hamiltonian_is_not_imitable():
    A = sparse_local_matrix(128)
    assert low_rank_imitability(A, 8) > 0.8
    assert stable_rank(A) > 10 * stable_rank(low_rank_matrix(128, 8))


def test_imitability_degrades_as_the_rank_rises():
    errs = [low_rank_imitability(low_rank_matrix(128, r), 8)
            for r in (8, 16, 32, 64)]
    assert errs == sorted(errs)
