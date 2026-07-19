"""Tests pinning the width-scan MPS machinery."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t6_2d_scan import SV, build2d, mpo_conjugate_2d, h_mpo_2d  # noqa
from t6_width_scan import mpo_mps_expect, mps_from_dense  # noqa: E402


def test_mps_reconstruction_exact():
    rng = np.random.default_rng(1)
    psi = rng.normal(size=64) + 1j * rng.normal(size=64)
    psi /= np.linalg.norm(psi)
    A, disc = mps_from_dense(psi, 6)
    assert disc < 1e-12
    # reconstruct
    T = A[0]
    for t in A[1:]:
        T = np.einsum('...a,abc->...bc', T, t)
    assert np.abs(T.reshape(-1) - psi).max() < 1e-10


def test_mps_mpo_expectation_matches_dense():
    P = build2d(2, 3)
    sv = SV(P)
    A, _ = mps_from_dense(sv.psi0, 6)
    v = float(np.real(mpo_mps_expect(h_mpo_2d(P), A)))
    assert abs(v - sv.emin) < 1e-8      # <psi0|H|psi0> = E_min


def test_mps_route_matches_exact_after_conjugation():
    P = build2d(2, 3, K=2, M=2)
    sv = SV(P)
    rng = np.random.default_rng(3)
    th = rng.uniform(-0.8, 0.8, 2)
    A, _ = mps_from_dense(sv.psi0, 6)
    Ws = mpo_conjugate_2d(P, th, 64)
    v = float(np.real(mpo_mps_expect(Ws, A)))
    assert abs(v - sv.loss(th)) < 1e-8


def test_truncated_mps_loses_fidelity_gracefully():
    rng = np.random.default_rng(5)
    psi = rng.normal(size=256) + 1j * rng.normal(size=256)
    psi /= np.linalg.norm(psi)
    _, d_full = mps_from_dense(psi, 8)
    _, d_cap = mps_from_dense(psi, 8, chi=2)
    assert d_full < 1e-12 and d_cap > 1e-3   # random state: chi=2 lossy
