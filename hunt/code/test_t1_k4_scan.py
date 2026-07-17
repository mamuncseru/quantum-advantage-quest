"""Tests pinning the K4-scan machinery (t1_k4_scan.py).

The scan's verdict is only as good as its instrument: these pin the
block-surrogate construction against exactly-known cases.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t1_k4_scan import (Ctx, box, config_stats, majorana_perm,  # noqa: E402
                        module_block, op_moment0, op_trace_with)


def dense(pc, dim):
    p, c = pc
    M = np.zeros((dim, dim), dtype=complex)
    M[p, np.arange(dim)] = c
    return M


def test_majoranas_anticommute_and_square_to_one():
    n, dim = 4, 16
    cs = [dense(majorana_perm(n, a), dim) for a in range(2 * n)]
    for a in range(2 * n):
        assert np.abs(cs[a] @ cs[a] - np.eye(dim)).max() < 1e-12
        for b in range(a + 1, 2 * n):
            assert np.abs(cs[a] @ cs[b] + cs[b] @ cs[a]).max() < 1e-12


def test_module_basis_hermitian_orthonormal():
    ctx = Ctx(4)
    dim = ctx.dim
    mats = [dense(pc, dim) for pc in ctx.B]
    assert len(mats) == 4 * (2 * 4 - 1) // 1 // 1 and len(mats) == 28
    for i, A in enumerate(mats):
        assert np.abs(A - A.conj().T).max() < 1e-12
        for j, B in enumerate(mats):
            ip = np.trace(A.conj().T @ B) / dim
            assert abs(ip - (1.0 if i == j else 0.0)) < 1e-12


def test_block_equals_total_without_box():
    ctx = Ctx(5)
    U = np.eye(ctx.dim, dtype=complex)
    T, mass2 = module_block(ctx, U)
    assert abs(mass2 - 1.0) < 1e-8
    assert np.abs(T - np.eye(ctx.mod)).max() < 1e-8
    _, _, vr, _ = config_stats(ctx, U, T, samples=6,
                               rng=np.random.default_rng(1))
    assert vr < 1e-12


def test_box_is_unitary_and_leaks():
    ctx = Ctx(5)
    U = box(5, 2, np.random.default_rng(3))
    assert np.abs(U @ U.conj().T - np.eye(32)).max() < 1e-10
    _, mass2 = module_block(ctx, U)
    assert mass2 < 0.6            # nonlocal depth-2 leaks the module


def test_moments_are_z_products_only():
    ctx = Ctx(4)
    # <0|i c_a c_b|0> is nonzero exactly for the n on-site pairs (Z_i)
    nz = sum(abs(op_moment0(pc)) > 1e-12 for pc in ctx.B)
    assert nz == 4
    for pc in ctx.B:
        v = op_moment0(pc)
        assert abs(v) < 1e-12 or abs(abs(v) - 1) < 1e-12
