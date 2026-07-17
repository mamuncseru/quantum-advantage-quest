"""Tests pinning the J1 shell-state lemma's exact validation.

If any of these move, the lemma's claims (composition exactness, the
sqrt(p) cancellation, payoff realization) must be re-derived — see
strike/j1-shell-preparation.md.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import j1_shell_state as j1  # noqa: E402


def build(seed=2):
    F, g = j1.make_instance(seed)
    h = j1.unit_fourier(g)
    return F, g, h


def test_recentring_gives_zero_dc_and_unit_states():
    _, g, h = build()
    for gi, hi in zip(g, h):
        assert abs(gi.sum()) < 1e-12
        assert abs(hi[0]) < 1e-12
        assert abs(np.linalg.norm(hi) - 1) < 1e-12


def test_composition_is_exact_and_ancillas_disentangle():
    _, _, h = build()
    w = np.array([0.5, -0.7, 0.6])
    w /= np.linalg.norm(w)
    a = j1.circuit_route(w, h)     # asserts ancilla disentanglement inside
    b = j1.definition_route(w, h)
    assert np.abs(a - b).max() < 1e-14
    assert abs(np.linalg.norm(a) - 1) < 1e-12


def test_dictionary_sqrt_p_cancellation():
    _, g, h = build()
    w = np.array([0.3, 0.8, -0.52])
    w /= np.linalg.norm(w)
    psi = j1.definition_route(w, h)
    u = j1.x_side(j1.to_frequency(psi))
    t = j1.target_x(w, g)
    u = u.real / np.linalg.norm(u)
    t = t / np.linalg.norm(t)
    if np.dot(u, t) < 0:
        u = -u
    assert np.abs(u - t).max() < 1e-13


def test_payoff_equals_pencil_top_eigenvalue():
    F, g, h = build()
    f, wopt, lam = j1.pencil(F, g)
    ef = j1.state_payoff(j1.definition_route(wopt, h), f, g)
    assert abs(ef - lam) < 1e-12
    # and no other weight vector tested does better (top-eigenvalue sanity)
    rng = np.random.default_rng(0)
    for _ in range(20):
        w = rng.normal(size=3)
        w /= np.linalg.norm(w)
        assert j1.state_payoff(j1.definition_route(w, h), f, g) <= lam + 1e-9


def test_second_instance_seed():
    # guard against seed luck: the exactness is structural
    F, g = j1.make_instance(seed=7)
    h = j1.unit_fourier(g)
    w = np.array([0.2, -0.6, 0.775])
    w /= np.linalg.norm(w)
    a = j1.circuit_route(w, h)
    b = j1.definition_route(w, h)
    assert np.abs(a - b).max() < 1e-14
