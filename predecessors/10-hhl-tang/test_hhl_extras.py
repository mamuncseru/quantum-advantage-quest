"""Tests for the tolls and for the dequantisation boundary.

Three carry the page: `test_the_solve_never_reads_the_whole_matrix` (the
audit that makes the dequantisation claim mean anything),
`test_readout_makes_hhl_strictly_worse_than_cg` (toll 3, priced), and
`test_sample_cost_tracks_rank_not_dimension` (the boundary, which is also
the regime a real advantage could live in).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from dequantize import (SQAccess, make_matrix, relative_error, rows_needed,
                        rows_needed_median, solve_quality, sq_low_rank_basis,
                        sq_sketch, sq_solve, stable_rank, true_pseudo_solve)
from hhl_tolls import (classical_cg_runtime, condition_number,
                       crossover_dimension, hhl_runtime,
                       hhl_with_readout_runtime, readout_penalty, random_spd,
                       samples_to_read_one_amplitude,
                       samples_to_read_the_whole_vector, sparse_spd)


# ==================================================== the tolls ============

def test_reading_one_number_is_dimension_free():
    """The case HHL is genuinely good at — and note that the answer is then
    a single number, not a solution vector."""
    a = samples_to_read_one_amplitude(0.01)
    assert a == samples_to_read_one_amplitude(0.01)
    assert 1e4 < a < 1e5


@pytest.mark.parametrize("dim", [10 ** 3, 10 ** 6])
def test_reading_the_vector_costs_the_dimension(dim):
    cheap = samples_to_read_one_amplitude(0.01)
    dear = samples_to_read_the_whole_vector(dim, 0.01)
    assert dear > dim * cheap / 10          # the dim factor is really there


def test_the_laplacian_condition_number_grows_quadratically():
    """'Well-conditioned' is an assumption, not a fact. The textbook sparse
    system has kappa ~ dim^2, which eats the log(dim) advantage outright."""
    dims = np.array([16, 32, 64, 128, 256], dtype=float)
    ks = np.array([condition_number(sparse_spd(int(d))) for d in dims])
    slope = np.polyfit(np.log(dims), np.log(ks), 1)[0]
    assert slope == pytest.approx(2.0, abs=0.15)


def test_random_spd_has_the_condition_number_it_was_asked_for():
    for kappa in (10, 100, 1000):
        assert condition_number(random_spd(60, kappa)) == pytest.approx(
            kappa, rel=1e-6)


def test_hhl_is_logarithmic_in_dimension_and_linear_in_kappa():
    base = hhl_runtime(2 ** 10, 100, 1e-6)
    assert hhl_runtime(2 ** 20, 100, 1e-6) == pytest.approx(2 * base)
    assert hhl_runtime(2 ** 10, 200, 1e-6) == pytest.approx(2 * base)


def test_conjugate_gradients_pays_only_the_square_root_of_kappa():
    """The comparison that matters and rarely appears: CG needs
    sqrt(kappa) iterations where the quantum algorithm needs kappa."""
    base = classical_cg_runtime(1000, 100, 1e-6)
    assert classical_cg_runtime(1000, 400, 1e-6) == pytest.approx(2 * base)


@pytest.mark.parametrize("dim,kappa", [(10 ** 3, 10), (10 ** 6, 10),
                                       (10 ** 6, 10 ** 4)])
def test_readout_makes_hhl_strictly_worse_than_cg(dim, kappa):
    """Toll 3, priced. When both sides return the vector there is no
    crossover at all — the quantum side pays kappa where CG pays its square
    root, and then pays dim/eps^2 to look at its own answer."""
    assert readout_penalty(dim, kappa) > 1e6
    assert hhl_with_readout_runtime(dim, kappa, 1e-3) > \
        classical_cg_runtime(dim, kappa, 1e-3)


def test_the_penalty_grows_with_the_dimension():
    small = readout_penalty(10 ** 3, 100)
    large = readout_penalty(10 ** 6, 100)
    assert large > small


def test_the_unfair_crossover_moves_right_as_kappa_grows():
    """Even the generous comparison does not behave like an exponential
    speedup: harder problems push the crossover further out."""
    ds = [crossover_dimension(k) for k in (10, 100, 10 ** 4, 10 ** 6)]
    assert ds == sorted(ds)


# ============================================== the access model ==========

def test_sq_access_samples_proportional_to_squared_row_norms():
    A = make_matrix(60, 40, rank=5, seed=1)
    sq = SQAccess(A, seed=2)
    idx, p = sq.sample_row(size=40000)
    counts = np.bincount(idx, minlength=60) / 40000.0
    assert np.abs(counts - p).max() < 0.02


def test_the_sketch_is_unbiased():
    """E[S^T S] = A^T A — the identity that IS the dequantisation, checked by
    sampling rather than by algebra."""
    A = make_matrix(40, 25, rank=4, seed=3)
    acc = np.zeros((25, 25))
    trials = 300
    for t in range(trials):
        S, _, _ = sq_sketch(SQAccess(A, seed=t), 12)
        acc += S.T @ S
    acc /= trials
    assert np.abs(acc - A.T @ A).max() / np.abs(A.T @ A).max() < 0.15


def test_the_solve_never_reads_the_whole_matrix():
    """The audit that makes the whole claim meaningful: the query counter
    proves the classical algorithm touched only the rows it sampled."""
    m = n = 300
    A = make_matrix(m, n, rank=5, seed=4)
    rng = np.random.default_rng(0)
    b = A @ rng.normal(size=n)
    sq = SQAccess(A, seed=5)
    sq_solve(sq, b, 5, 20)
    assert sq.queries <= 21 * n            # 20 sampled rows, nothing else
    assert sq.queries < 0.1 * m * n


def test_more_rows_reduce_the_error():
    errs = [solve_quality(300, 300, 5, 5, r, seed=6)[0]
            for r in (8, 32, 128)]
    assert errs[0] > errs[-1]
    assert errs[-1] < 0.15


def test_the_dequantised_solve_returns_a_vector_not_a_state():
    """Stated as a test because it is the asymmetry the comparison turns on:
    the classical output is the thing you wanted."""
    m = n = 200
    A = make_matrix(m, n, rank=4, seed=7)
    rng = np.random.default_rng(1)
    b = A @ rng.normal(size=n)
    x = sq_solve(SQAccess(A, seed=8), b, 4, 40)
    assert x.shape == (n,)
    assert relative_error(x, true_pseudo_solve(A, b, 4)) < 0.3


# ============================================== where it stops ============

def test_sample_cost_tracks_rank_not_dimension():
    """The boundary. Rows needed grows with the rank; a bigger matrix of the
    same rank does not cost more."""
    small = rows_needed_median(200, 200, 10, target=0.15, seeds=3)
    big = rows_needed_median(600, 600, 10, target=0.15, seeds=3)
    assert big <= 2.5 * small                       # dimension barely matters
    low = rows_needed_median(400, 400, 10, target=0.1, seeds=3)
    high = rows_needed_median(400, 400, 80, target=0.1, seeds=3)
    assert high > 2 * low                           # rank matters a lot


def test_stable_rank_is_the_variable_sampling_responds_to():
    """Nominal rank counts directions; stable rank weighs them. A rank-2
    matrix whose weight sits in one direction is *harder* to sketch than a
    rank-10 one — which is why 'low rank means dequantisable' needs care."""
    sr2 = stable_rank(make_matrix(400, 400, 2, seed=0))
    sr10 = stable_rank(make_matrix(400, 400, 10, seed=0))
    assert sr2 < 2.0 < sr10
    hard = rows_needed_median(400, 400, 2, target=0.1, seeds=5)
    easy = rows_needed_median(400, 400, 10, target=0.1, seeds=5)
    assert hard > easy


def test_stable_rank_is_about_half_the_nominal_rank_for_this_spectrum():
    for rank in (10, 20, 40):
        sr = stable_rank(make_matrix(400, 400, rank, seed=0))
        assert 0.3 * rank < sr < 0.6 * rank


def test_high_rank_defeats_the_sketch():
    """Push the rank up and the classical shortcut disappears — which is the
    regime where a quantum advantage is still possible."""
    need = rows_needed(400, 400, 200, target=0.1, seed=0)
    assert need is None or need > 100
