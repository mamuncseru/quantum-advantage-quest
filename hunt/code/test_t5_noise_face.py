"""Tests pinning the T5 noise-face instrument (two independent noisy
arms must agree exactly)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t5_noise_face import NoisyInst  # noqa: E402


def _theta(inst, seed=1):
    return np.random.default_rng(seed).uniform(-0.3, 0.3, inst.nparam)


def test_noiseless_reduces_to_statevector():
    inst = NoisyInst(6, 0.0)
    th = _theta(inst)
    assert abs(inst.noisy_loss(th) - inst.exact_loss(th)) < 1e-10


def test_density_matrix_physical_under_noise():
    inst = NoisyInst(6, 0.02)
    rho = inst.rho_final(_theta(inst))
    assert abs(np.trace(rho) - 1) < 1e-10
    assert np.abs(rho - rho.conj().T).max() < 1e-10
    assert np.linalg.eigvalsh(rho).min() > -1e-10


def test_damped_propagation_matches_density_matrix():
    # two independent implementations of the noisy loss
    for p in (0.005, 0.02):
        inst = NoisyInst(6, p)
        th = _theta(inst, seed=3)
        assert abs(inst.noisy_loss(th)
                   - inst.noisy_surrogate(th, None)) < 1e-10


def test_noise_contracts_toward_maximally_mixed():
    # heavy noise: loss approaches Tr[H]/2^n = 0 (traceless H)
    inst = NoisyInst(6, 0.3)
    th = _theta(inst, seed=5)
    assert abs(inst.noisy_loss(th)) < abs(NoisyInst(6, 0.0).noisy_loss(th))


def test_budget_well_defined_under_noise():
    inst = NoisyInst(6, 0.01)
    nb = inst.noisy_budget(_theta(inst, seed=7), tol=0.1)
    assert nb is not None
