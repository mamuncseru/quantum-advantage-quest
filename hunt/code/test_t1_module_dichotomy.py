"""Tests pinning T1's first numerics (module dichotomy).

Fast versions of the brief's exhibits — if any changes character, the
T1 pre-registration must be revisited.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import t1_module_dichotomy as t1  # noqa: E402


def test_generators_live_in_the_quadratic_module():
    # the bug the first draft had: ansatz generators must be quadratic
    for H in (t1.HXX, t1.HZ):
        coeffs = [t1.hs(B, H) for B in t1.DEG2]
        R = H - sum(c * B for c, B in zip(coeffs, t1.DEG2))
        assert np.abs(R).max() < 1e-10


def test_gsim_surrogate_exact():
    assert t1.gsim_exhibit(trials=5) < 1e-10


def test_parity_sector_is_invariant_hence_untrainable():
    P = t1.monomial(tuple(range(2 * t1.N)))     # fermion parity
    for H in (t1.HXX, t1.HZ):
        assert np.abs(H @ P - P @ H).max() < 1e-10


def test_block_surrogate_exact_without_box():
    rows = t1.interleaved_scan(depths=(0,), samples=5)
    assert rows[0]["block_err"] < 1e-10
    assert rows[0]["m2"] > 1 - 1e-10


def test_nonlocal_box_leaks_at_depth_one():
    rows = t1.interleaved_scan(depths=(1,), samples=5, local=False)
    assert rows[0]["m2"] < 0.5                  # module collapses
    assert rows[0]["budget"] > 500              # sector budget explodes
    assert rows[0]["var_th"] > 1e-3             # gradients stay alive


def test_ad_closure_module_only_without_box():
    U = np.eye(t1.DIM, dtype=complex)
    dim, capped = t1.ad_closure_dim(U, cap=200)
    assert dim == 66 and not capped
