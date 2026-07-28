"""Tests for autopsy 04's two experiments and the page's widget physics.

Independent of shor.py's own tests; nothing here modifies the reference
implementation.
"""

import cmath
import sys
from math import gcd
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from shor import find_order                                  # noqa: E402
from shor_compiled_cheat import (is_power_of_two, nontrivial_gates,  # noqa
                                 order, survey, units, useful)
from shor_resources import arithmetic_cost, circuit_shape, feasibility  # noqa


# ---- the reduction (section 2) --------------------------------------

@pytest.mark.parametrize("N", [15, 21, 33, 35, 39])
def test_reduction_finds_a_factor_for_at_least_half_the_bases(N):
    us = units(N)
    good = [a for a in us if useful(a, N)]
    assert len(good) / len(us) >= 0.5           # the "probability >= 1/2"
    for a in good:                              # and they really are factors
        r = order(a, N)
        x = pow(a, r // 2, N)
        f = next(g for g in (gcd(x - 1, N), gcd(x + 1, N)) if 1 < g < N)
        assert N % f == 0


def test_order_matches_definition():
    for N in (15, 21, 35):
        for a in units(N):
            r = order(a, N)
            assert pow(a, r, N) == 1
            assert all(pow(a, k, N) != 1 for k in range(1, r))


# ---- the compiled-demo claim (section 8) ----------------------------

def test_cascade_collapses_exactly_when_order_is_a_power_of_two():
    for N in (15, 21, 35, 51):
        t = circuit_shape(N)["counting"]
        for a in units(N):
            r = order(a, N)
            gates = nontrivial_gates(a, N, t)
            if is_power_of_two(r):
                assert gates == max(1, r.bit_length() - 1)
                assert gates < t                # it really does collapse
            else:
                assert gates == t               # nothing collapses


def test_every_base_collapses_for_fifteen():
    _, rows = survey(15)
    assert all(r["collapses"] for r in rows)


@pytest.mark.parametrize("N,expected", [
    (15, True),    # 3 x 5     — Fermat primes
    (51, True),    # 3 x 17
    (85, True),    # 5 x 17
    (21, False),   # 3 x 7     — 7 is not a Fermat prime
    (35, False),   # 5 x 7
    (33, False),   # 3 x 11
])
def test_fermat_prime_criterion(N, expected):
    """Every base collapses iff N is a product of distinct Fermat primes."""
    us = units(N)
    all_collapse = all(is_power_of_two(order(a, N)) for a in us)
    assert all_collapse is expected


# ---- resource accounting (section 7) --------------------------------

def test_circuit_shape_matches_shor_py():
    s = circuit_shape(15)
    assert s == dict(N=15, work=4, counting=9, qubits=13, hadamards=9,
                     controlled_mults=9, qft_phase_gates=36)


def test_shor15_is_infeasible_on_every_machine():
    """The claim of section 7 — no machine survives the circuit."""
    prof, rows = feasibility(15)
    assert prof.qubits == 13
    assert 5000 < prof.g2 < 10000
    assert rows, "the catalog returned nothing"
    for r in rows:
        assert r["verdict"] != "RUNS"
        if r["fidelity"] > 0:
            assert r["fidelity"] < 0.05


def test_cost_model_scales_cubically():
    a = arithmetic_cost(bits=64)["toffoli"]
    b = arithmetic_cost(bits=128)["toffoli"]
    assert 7.0 < b / a < 9.0                    # ~2^3 for a cubic model


# ---- the widgets' physics -------------------------------------------

def _dft_probs(re, im):
    """Exact port of dftProbs() in docs/javascripts/qq-anim.js."""
    M = len(re)
    out = []
    for c in range(M):
        acc = 0j
        for j in range(M):
            acc += complex(re[j], im[j]) * cmath.exp(-2j * cmath.pi * j * c / M)
        out.append(abs(acc) ** 2 / M)
    return out


def _convergents(num, den, limit=12):
    """Exact port of convergents() in qq-anim.js."""
    out, a, b = [], num, den
    h0, h1, k0, k1 = 0, 1, 1, 0
    while b and len(out) < limit:
        q = a // b
        a, b = b, a - q * b
        h0, h1 = h1, q * h1 + h0
        k0, k1 = k1, q * k1 + k0
        out.append((q, h1, k1))
    return out


@pytest.mark.parametrize("r", [2, 4, 8])
def test_shorcomb_widget_peaks_land_on_multiples_of_M_over_r(r):
    """The 'shorcomb' widget claims a comb of spacing r transforms into
    peaks at multiples of 2^t/r (exact when r divides 2^t)."""
    t, M = 6, 64
    for j0 in range(r):
        re = [0.0] * M
        idx = list(range(j0, M, r))
        for i in idx:
            re[i] = 1 / np.sqrt(len(idx))
        p = _dft_probs(re, [0.0] * M)
        peaks = {c for c in range(M) if p[c] > 1e-9}
        assert peaks == {k * M // r for k in range(r)}
        for c in peaks:                          # and they are uniform
            assert np.isclose(p[c], 1.0 / r, atol=1e-9)


def test_contfrac_widget_recovers_the_order():
    """The 'contfrac' widget claims the largest convergent denominator
    below N is the order. N = 15, t = 6, r = 4 -> peaks at 0,16,32,48."""
    M, N, r = 64, 15, 4
    for c in (16, 32, 48):
        best = None
        for _, num, den in _convergents(c, M):
            if den <= N:
                best = den
        assert r % best == 0                     # a divisor of r (or r)
    assert max(den for _, _, den in _convergents(16, M) if den <= N) == 4


def test_modorder_widget_arithmetic():
    """The 'modorder' widget claims the chain returns to 1 after r steps
    and that the gcd step then yields a factor."""
    N, a = 15, 7
    v, chain = 1, [1]
    for _ in range(order(a, N)):
        v = (v * a) % N
        chain.append(v)
    assert chain == [1, 7, 4, 13, 1]
    r = order(a, N)
    x = pow(a, r // 2, N)
    assert (x * x) % N == 1
    assert sorted({gcd(x - 1, N), gcd(x + 1, N)}) == [3, 5]


def test_widget_order_agrees_with_the_simulator():
    """The widgets' classical order must match what the quantum circuit
    actually recovers."""
    for N, a in ((15, 7), (15, 2), (21, 2)):
        assert find_order(a, N, shots=40, seed=3) == order(a, N)
