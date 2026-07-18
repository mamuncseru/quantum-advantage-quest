"""Tests pinning the T6 control-window instrument (three arms must
agree: statevector, truncated propagation, dense conjugation)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import t6_control_window as t6  # noqa: E402


def short(monkey_k=1, monkey_m=1):
    t6.K, t6.M_TROT = monkey_k, monkey_m
    rng = np.random.default_rng(2)
    return rng.uniform(-0.5, 0.5, monkey_k)


def teardown_function(_):
    t6.K, t6.M_TROT = 6, 3            # restore module protocol


def test_propagation_matches_statevector():
    th = short()
    for obj in t6.OBJ.values():
        assert abs(t6.surrogate_loss(th, obj, None)
                   - t6.loss(th, obj)) < 1e-10


def test_gate_list_order_matches_evolve():
    # the bug this instrument shipped with once: Trotter-order mismatch
    th = short(2, 2)
    for obj in t6.OBJ.values():
        assert abs(t6.surrogate_loss(th, obj, None)
                   - t6.loss(th, obj)) < 1e-10


def test_dense_conjugation_matches_loss():
    th = short(2, 2)
    b = np.arange(t6.DIM)
    O = np.zeros((t6.DIM, t6.DIM), complex)
    for (x, z), c in t6.MST.items():
        O[b ^ x, b] += c * ((1j) ** int(x & z).bit_count() * t6.zdiag(z))
    for (gx, gz, thg) in reversed(t6.gate_list(th)):
        ph = (1j) ** int(gx & gz).bit_count() * t6.zdiag(gz)
        PO = np.empty_like(O)
        PO[b ^ gx, :] = ph[:, None] * O
        OP = np.empty_like(O)
        OP[:, b ^ gx] = O * ph[None, :]
        POP = np.empty_like(PO)
        POP[:, b ^ gx] = PO * ph[None, :]
        c1, s1 = np.cos(thg), np.sin(thg)
        O = c1 * c1 * O + s1 * s1 * POP + 1j * c1 * s1 * (PO - OP)
    val = float(np.real(t6.PSI0.conj() @ (O @ t6.PSI0)))
    assert abs(val - t6.loss(th, t6.MST)) < 1e-10


def test_ground_state_is_stationary_without_drive():
    # theta = 0 evolves under H's own Trotterization: <H> nearly constant
    t6.K, t6.M_TROT = 2, 3
    th = np.zeros(2)
    e0 = t6.expect(t6.PSI0, t6.HTERMS)
    eT = t6.loss(th, t6.HTERMS)
    # first-order Trotter at dt=0.1, ||H|| ~ 12: drift ~0.2 is physics,
    # not a bug — bound it at ~4% of |E_min|
    assert abs(eT - e0) < 0.5


def test_op_entanglement_grows_from_local_start():
    th0 = short(1, 1)
    s_short = t6.op_entanglement(th0, t6.MST)
    t6.K, t6.M_TROT = 4, 3
    s_long = t6.op_entanglement(np.full(4, 0.7), t6.MST)
    assert s_long > s_short           # spreading increases the proxy
