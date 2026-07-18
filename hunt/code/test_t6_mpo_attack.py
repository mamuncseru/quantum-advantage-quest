"""Tests pinning the K4-t6 MPO machinery (hand-built, so every piece is
checked against dense at the n=6 exactness point, chi = 64 = 4^3)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t6_mpo_attack import (build, compress, dense_evolved, dense_H,  # noqa
                           ground_state, h_mpo, mpo_add, mpo_apply,
                           mpo_loss, mpo_to_dense)


def test_h_mpo_exact():
    for n in (4, 6):
        P = build(n)
        assert np.abs(mpo_to_dense(h_mpo(P)) - dense_H(P)).max() < 1e-12


def test_mpo_apply_matches_dense():
    P = build(6)
    rng = np.random.default_rng(0)
    psi = rng.normal(size=64) + 1j * rng.normal(size=64)
    psi /= np.linalg.norm(psi)
    assert np.abs(mpo_apply(h_mpo(P), psi)
                  - dense_H(P) @ psi).max() < 1e-12


def test_add_and_compress_preserve_operator():
    P = build(5)
    A, B = h_mpo(P), h_mpo(P)
    S = mpo_add(A, B)
    dense_sum = mpo_to_dense(compress(S, chi=64))
    assert np.abs(dense_sum - 2 * dense_H(P)).max() < 1e-10


def test_full_pipeline_exact_at_n6():
    P = build(6, K=2, M=2)
    rng = np.random.default_rng(3)
    th = rng.uniform(-0.8, 0.8, 2)
    psi, _ = ground_state(P)
    ref = dense_evolved(P, th, dense_H(P))
    vref = float(np.real(psi.conj() @ (ref @ psi)))
    assert abs(mpo_loss(P, th, 64, psi) - vref) < 1e-10


def test_truncation_degrades_gracefully():
    P = build(6, K=2, M=2)
    rng = np.random.default_rng(5)
    th = rng.uniform(-0.8, 0.8, 2)
    psi, _ = ground_state(P)
    ref = dense_evolved(P, th, dense_H(P))
    vref = float(np.real(psi.conj() @ (ref @ psi)))
    e4 = abs(mpo_loss(P, th, 4, psi) - vref)
    e64 = abs(mpo_loss(P, th, 64, psi) - vref)
    assert e64 < 1e-10 and e64 <= e4
