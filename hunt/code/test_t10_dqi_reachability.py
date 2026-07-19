"""Tests pinning the T10 instrument."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import t10_dqi_reachability as t10  # noqa: E402


def test_constraints_are_weight_three_parities():
    assert len(t10.ROWS) == t10.M_CONS
    for r in t10.ROWS:
        assert int(r).bit_count() == 3
    assert set(np.unique(t10.G)) <= {-1.0, 1.0}


def test_fval_consistent_with_signs():
    # f = (m + sum g_i)/2 pointwise
    ref = (t10.M_CONS + t10.G.sum(axis=0)) / 2
    assert np.abs(ref - t10.FVAL).max() < 1e-12


def test_dqi_curve_monotone_and_bounded():
    c = t10.dqi_curve()
    vals = [c[k] for k in sorted(c)]
    assert all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))
    assert 0.5 < vals[0] and vals[-1] <= t10.FMAX / t10.M_CONS + 1e-9


def test_qaoa_uniform_state_gives_random_payoff():
    val = t10.qaoa_payoff(np.zeros(2))
    assert abs(val / t10.M_CONS - t10.FVAL.mean() / t10.M_CONS) < 1e-10


def test_budget_arm_untruncated_exact():
    rng = np.random.default_rng(5)
    th = rng.uniform(0, 0.6, 4)
    assert t10.qaoa_budget(th, tol=1e-9, ladder=(10 ** 9,)) is not None
