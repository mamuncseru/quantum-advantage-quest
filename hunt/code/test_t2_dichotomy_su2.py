"""Tests pinning T2's su(2) validation of the dichotomy lemmas."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import t2_dichotomy_su2 as t2  # noqa: E402


def test_multiplicities_match_commutant():
    # 5 spins-1/2: state-space spin content j=5/2 x1, 3/2 x4, 1/2 x5
    # => operator invariants k_0 = 1^2+4^2+5^2 = 42
    ks = {l: t2.TBASIS[l].shape[0] for l in t2.TBASIS}
    assert ks[0] == 42
    assert sum(k * (2 * l + 1) for l, k in ks.items()) == t2.OP


def test_components_complete_and_isometric():
    rng = np.random.default_rng(5)
    A = rng.normal(size=(t2.DIM, t2.DIM)) \
        + 1j * rng.normal(size=(t2.DIM, t2.DIM))
    total = sum(float(np.sum(np.abs(c) ** 2))
                for c in t2.components(A).values())
    assert abs(total - float(np.sum(np.abs(A) ** 2))) < 1e-8


def test_contraction_surrogate_exact():
    rng = np.random.default_rng(9)
    psi = rng.normal(size=t2.DIM) + 1j * rng.normal(size=t2.DIM)
    psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi.conj())
    O = t2.JX @ t2.JX - t2.JZ + np.diag(rng.normal(size=t2.DIM))
    O = (O + O.conj().T) / 2
    M = t2.cross_moments(rho, O)
    for _ in range(5):
        p = rng.uniform(-np.pi, np.pi, 2 * t2.LAYERS)
        assert abs(t2.surrogate_loss(M, p)
                   - t2.exact_loss(rho, O, p)) < 1e-10


def test_invariant_sector_is_constant():
    rng = np.random.default_rng(3)
    psi = rng.normal(size=t2.DIM) + 1j * rng.normal(size=t2.DIM)
    psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi.conj())
    M = t2.cross_moments(rho, t2.JZ @ t2.JZ + t2.JX @ t2.JX
                         + t2.JY @ t2.JY)          # Casimir: pure l=0
    vals = [t2.surrogate_loss(M, rng.uniform(-np.pi, np.pi,
                                             2 * t2.LAYERS))
            for _ in range(10)]
    assert np.var(vals) < 1e-20


def test_variance_law_order_of_magnitude():
    rng = np.random.default_rng(11)
    psi = rng.normal(size=t2.DIM) + 1j * rng.normal(size=t2.DIM)
    psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi.conj())
    M = t2.cross_moments(rho, t2.JX @ t2.JX - t2.JZ)
    for l in (1, 2):
        vals = [t2.surrogate_loss({l: M[l]},
                                  rng.uniform(-np.pi, np.pi,
                                              2 * t2.LAYERS))
                for _ in range(300)]
        pred = float(np.linalg.norm(M[l]) ** 2) / (2 * l + 1)
        assert pred / 3 < np.var(vals) < pred * 3
