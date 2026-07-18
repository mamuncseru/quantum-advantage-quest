"""Tests pinning the T4 adaptive-growth instrument."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t4_adaptive_growth import (Inst, adapt_run, anticommute,  # noqa: E402
                                pmult, _pauli_dense, rotosolve)


def test_pauli_product_phase_against_dense():
    rng = np.random.default_rng(3)
    for _ in range(30):
        x1, z1, x2, z2 = (int(v) for v in rng.integers(0, 8, 4))
        x3, z3, ph = pmult(x1, z1, x2, z2)
        ref = _pauli_dense(x1, z1, 3) @ _pauli_dense(x2, z2, 3)
        assert np.abs(ph * _pauli_dense(x3, z3, 3) - ref).max() < 1e-9


def test_anticommute_matches_dense():
    rng = np.random.default_rng(5)
    for _ in range(20):
        x1, z1, x2, z2 = (int(v) for v in rng.integers(0, 8, 4))
        A, B = _pauli_dense(x1, z1, 3), _pauli_dense(x2, z2, 3)
        anti = np.abs(A @ B + B @ A).max() < 1e-9
        assert anticommute(x1, z1, x2, z2) == (1 if anti else 0)


def test_engine_and_pool_grads_match_exact():
    for ham in ("A", "B"):
        inst = Inst(6, ham)
        rng = np.random.default_rng(1)
        gates = [(inst.pool[i][0], inst.pool[i][1], rng.uniform(-1, 1))
                 for i in rng.integers(0, len(inst.pool), 5)]
        assert abs(inst.surrogate_loss(gates, None)
                   - inst.exact_loss(gates)) < 1e-10
        ge = inst.exact_pool_grads(gates)
        gs = inst.surrogate_pool_grads(gates, None)
        assert max(abs(a - b) for a, b in zip(ge, gs)) < 1e-10


def test_rotosolve_finds_sinusoid_minimum():
    inst = Inst(5, "A")
    gates = [(inst.pool[0][0], inst.pool[0][1], 0.0)]
    rotosolve(inst.exact_loss, gates, 0)
    th = gates[0][2]
    for d in (-0.1, 0.1):
        g2 = [(gates[0][0], gates[0][1], th + d)]
        assert inst.exact_loss(g2) >= inst.exact_loss(gates) - 1e-9


def test_adapt_descends():
    inst = Inst(6, "A")
    g, _ = adapt_run(inst, rounds=6)
    assert inst.exact_loss(g) < inst.exact_loss([]) - 1.0
