"""Tests pinning the 2D control instrument (T6 continuation)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from t6_2d_scan import (SV, build2d, h_mpo_2d, mpo_loss_2d,  # noqa: E402
                        pauli_surrogate)
from t6_mpo_attack import mpo_to_dense  # noqa: E402


def test_snake_ordering_covers_lattice():
    P = build2d(4, 4)
    assert P["n"] == 16 and len(P["bonds"]) == 24
    assert sorted(set(sum(([a, b] for a, b in P["bonds"]), []))) \
        == list(range(16))


def test_h_mpo_matches_matvec():
    P = build2d(2, 3)
    sv = SV(P)
    Hd = mpo_to_dense(h_mpo_2d(P))
    rng = np.random.default_rng(1)
    v = rng.normal(size=sv.dim) + 1j * rng.normal(size=sv.dim)
    assert np.abs(Hd @ v - sv.hv(v)).max() < 1e-10


def test_pauli_and_mpo_arms_match_exact_at_2x3():
    P = build2d(2, 3, K=2, M=2)
    sv = SV(P)
    rng = np.random.default_rng(3)
    th = rng.uniform(-0.8, 0.8, 2)
    ex = sv.loss(th)
    assert abs(pauli_surrogate(sv, th, None) - ex) < 1e-10
    assert abs(mpo_loss_2d(sv, th, 64) - ex) < 1e-10


def test_ground_state_energy_sane():
    sv = SV(build2d(2, 3))
    # 2D TFIM at g=3: paramagnetic-ish; E_min per site between -g-4 and -g
    per = sv.emin / 6
    assert -7.0 < per < -3.0
