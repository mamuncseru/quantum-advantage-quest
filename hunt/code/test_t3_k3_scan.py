"""Tests pinning the K3-scan instrument (n-generic warm-start budgets)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t3_k3_scan import Inst, budget_needed  # noqa: E402


def test_engine_matches_statevector():
    inst = Inst(6)
    rng = np.random.default_rng(0)
    p = rng.uniform(-0.3, 0.3, inst.nparam)
    assert abs(inst.surrogate_loss(p, None) - inst.exact_loss(p)) < 1e-10


def test_ground_energy_against_dense_reference():
    inst = Inst(6)
    # independent dense build from the Pauli terms
    from t3_warmstart_budget import PAULI

    def pauli_dense(x, z, n):
        M = np.array([[1]], dtype=complex)
        for q in range(n):
            a = ((x >> q) & 1) + 2 * ((z >> q) & 1)
            M = np.kron(PAULI[{0: 0, 1: 1, 2: 3, 3: 2}[a]], M)
        return M

    H = sum(c * pauli_dense(x, z, 6) for (x, z), c in inst.terms.items())
    ref = float(np.linalg.eigvalsh(H)[0].real)
    assert abs(inst.emin - ref) < 1e-8


def test_bitwise_count_uint8_underflow_guarded():
    # the bug this instrument shipped with once: uint8 sign underflow
    inst = Inst(6)
    assert inst.diag.min() >= -10 and inst.diag.max() <= 10
    assert abs(inst.diag.sum()) < 1e-9          # traceless


def test_matvec_matches_dense_diag_plus_flips():
    inst = Inst(5)
    rng = np.random.default_rng(2)
    v = rng.normal(size=inst.dim)
    hv = inst._hv(v)
    ref = inst.diag * v
    b = np.arange(inst.dim)
    for x, c in inst.xflips:
        ref = ref + c * v[b ^ x]
    assert np.abs(hv - ref).max() < 1e-12


def test_budget_needed_monotone_interface():
    inst = Inst(6)
    rng = np.random.default_rng(4)
    p = rng.uniform(-0.15, 0.15, inst.nparam)
    nb = budget_needed(inst, p, tol=0.0125 * 6)
    assert nb is not None and nb <= 2048       # warm point: cheap
