"""Tests pinning the T3 Pauli-propagation instrument."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import t3_warmstart_budget as t3  # noqa: E402


def test_engine_matches_statevector_untruncated():
    rng = np.random.default_rng(2)
    for _ in range(2):
        p = rng.uniform(-0.4, 0.4, t3.NPARAM)
        assert abs(t3.surrogate_loss(p, None) - t3.exact_loss(p)) < 1e-10


def test_identity_circuit_gives_diagonal_expectation():
    p = np.zeros(t3.NPARAM)
    # theta = 0: only CZs act, and CZ|0...0> = |0...0>
    expect = (t3.N - 1) * 1.0 + (t3.N - 2) * 0.4
    assert abs(t3.exact_loss(p) - expect) < 1e-10
    assert abs(t3.surrogate_loss(p, None) - expect) < 1e-10


def test_truncation_degrades_gracefully():
    rng = np.random.default_rng(7)
    p = rng.uniform(-np.pi, np.pi, t3.NPARAM)   # deep/generic point
    ex = t3.exact_loss(p)
    e_small = abs(t3.surrogate_loss(p, 32) - ex)
    e_big = abs(t3.surrogate_loss(p, 8192) - ex)
    assert e_big < e_small + 1e-9


def test_ground_energy_below_initial():
    assert t3.EMIN < t3.exact_loss(np.zeros(t3.NPARAM))


def test_spsa_shared_seed_deterministic():
    rng = np.random.default_rng(3)
    th0 = 0.1 * rng.normal(size=t3.NPARAM)
    a = t3.descend_spsa(t3.exact_loss, th0, 5, seed=9)
    b = t3.descend_spsa(t3.exact_loss, th0, 5, seed=9)
    assert np.allclose(a, b)
