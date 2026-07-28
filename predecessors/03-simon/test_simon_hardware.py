"""Tests for autopsy 03's two experiments and the page's widget physics."""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from simon import make_simon_function                       # noqa: E402
from simon_classical_attack import (birthday_hunt,          # noqa: E402
                                    break_linear,
                                    linear_simon_oracle)
from simon_on_hardware import (clean_fraction, collect_samples,  # noqa: E402
                               dot, majority_solve, naive_solve,
                               oracle_cnots, s_int)
from qsim.noise import MachineNoise                          # noqa: E402


# ---- the linear oracle and its classical break ----------------------

@pytest.mark.parametrize("n,s", [(4, 0b1011), (5, 0b10110), (6, 0b101101),
                                 (8, 0b10000001)])
def test_linear_oracle_is_two_to_one_with_the_right_mask(n, s):
    f = linear_simon_oracle(s, n)
    for x in range(2 ** n):
        assert f(x) == f(x ^ s)                  # the promise holds
    seen = {}
    for x in range(2 ** n):
        seen.setdefault(f(x), []).append(x)
    assert all(len(v) == 2 for v in seen.values())   # exactly 2-to-1


@pytest.mark.parametrize("n", [4, 6, 8, 12, 16])
def test_classical_attack_breaks_linear_oracle_in_n_queries(n):
    s_true = (1 << (n - 1)) | 0b1011
    s, queries = break_linear(linear_simon_oracle(s_true, n), n)
    assert s == s_true
    assert queries == n              # the whole point of section 6


def test_random_oracle_costs_the_birthday_bound():
    """Median collision-hunt cost should track 2^(n/2), not n."""
    rng = np.random.default_rng(5)
    med = {}
    for n in (6, 12):
        qs = []
        for t in range(15):
            f = make_simon_function(int(rng.integers(1, 2 ** n)), n,
                                    np.random.default_rng(t))
            s_found, q = birthday_hunt(f, n, rng)
            assert s_found is not None
            qs.append(q)
        med[n] = float(np.median(qs))
    # six extra bits of secret should cost roughly 2^3 = 8x more queries
    assert med[12] > 4 * med[6]
    assert med[12] < 40 * med[6]


# ---- the compiled circuit -------------------------------------------

def test_noiseless_samples_all_satisfy_the_constraint():
    n, s_bits = 5, [1, 0, 1, 1, 0]
    s = s_int(s_bits, n)
    ys = collect_samples(n, s_bits, None, shots=200, seed=2)
    assert clean_fraction(ys, s) == 1.0
    assert any(y != 0 for y in ys)               # not a degenerate state


def test_noiseless_solve_recovers_the_secret():
    for n, s_bits in [(4, [1, 0, 1, 1]), (5, [0, 1, 1, 0, 1])]:
        s = s_int(s_bits, n)
        ys = collect_samples(n, s_bits, None, shots=80, seed=6)
        assert naive_solve(ys, n) == s


def test_oracle_circuit_is_cnots_only_and_sized_right():
    n, s_bits = 5, [1, 0, 1, 1, 0]
    pairs = oracle_cnots(s_bits, n)
    assert len(pairs) == n + sum(s_bits)         # copy + fan-out
    for (c, t) in pairs:
        assert 0 <= c < n <= t < 2 * n           # input -> output only


def test_noise_corrupts_equations_and_majority_repairs_them():
    n, s_bits = 5, [1, 0, 1, 1, 0]
    s = s_int(s_bits, n)
    noise = MachineNoise.from_catalog("rigetti-ankaa-3")
    ys = collect_samples(n, s_bits, noise, shots=180, seed=8)
    cf = clean_fraction(ys, s)
    assert 0.85 < cf < 1.0                       # some equations are wrong
    assert majority_solve(ys, n) == s            # but the repair works


def test_helios_is_cleaner_than_ankaa():
    n, s_bits = 4, [1, 0, 1, 1]
    s = s_int(s_bits, n)
    a = clean_fraction(collect_samples(
        n, s_bits, MachineNoise.from_catalog("quantinuum-helios"),
        shots=120, seed=1), s)
    b = clean_fraction(collect_samples(
        n, s_bits, MachineNoise.from_catalog("rigetti-ankaa-3"),
        shots=120, seed=1), s)
    assert a >= b


# ---- the widgets' physics -------------------------------------------

def _walsh(a):
    """Exact port of walsh() in docs/javascripts/qq-anim.js."""
    N, ln = len(a), 1
    while ln < N:
        for i in range(0, N, ln << 1):
            for j in range(i, i + ln):
                u, v = a[j], a[j + ln]
                a[j] = (u + v) / math.sqrt(2)
                a[j + ln] = (u - v) / math.sqrt(2)
        ln <<= 1
    return a


@pytest.mark.parametrize("s", [0b1011, 0b0001, 0b1111, 0b0110])
def test_simoncomb_widget_kills_exactly_the_wrong_half(s):
    """The 'simoncomb' widget claims: after collapsing to a coset and
    applying H, every surviving y satisfies y·s = 0, and they are
    uniform."""
    n, N = 4, 16
    for x0 in range(N):
        a = [0.0] * N
        a[x0] = 1 / math.sqrt(2)
        a[x0 ^ s] = 1 / math.sqrt(2)
        out = _walsh(a)
        for y in range(N):
            if dot(y, s):
                assert abs(out[y]) < 1e-12          # annihilated exactly
            else:
                assert np.isclose(abs(out[y]), math.sqrt(2) / math.sqrt(N),
                                  atol=1e-12)       # uniform survivors


def test_coset_widget_pairing_is_an_involution():
    """The 'coset' widget claims 8 couples with one hidden step."""
    n, N, s = 4, 16, 0b1011
    partner = {x: x ^ s for x in range(N)}
    assert all(partner[partner[x]] == x for x in range(N))
    assert len({frozenset((x, partner[x])) for x in range(N)}) == N // 2


def test_constraints_widget_halves_the_candidate_set():
    """The 'constraints' widget claims each independent equation halves
    the suspects, ending at exactly one."""
    n, N, s = 4, 16, 0b1011
    alive = [c for c in range(1, N)]
    assert len(alive) == 15
    sizes = []
    for y in (0b1010, 0b1001, 0b0100):       # independent, all ⟂ s
        assert dot(y, s) == 0
        alive = [c for c in alive if dot(y, c) == 0]
        sizes.append(len(alive))
    assert sizes == [7, 3, 1]                # each equation halves it
    assert alive == [s]
