"""Tests for the compiled BV circuit (notes.md section 6) and for the
physics the page's interactive figures claim.

Deliberately independent of bernstein_vazirani.py, which is homework:
these tests must pass whether or not the exercise has been done.
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from bv_on_hardware import (exact_rate, majority_vote,      # noqa: E402
                            measure_shots, per_bit_rate, target_string)
from qsim.noise import MachineNoise                          # noqa: E402


# ---- the compiled circuit ------------------------------------------

@pytest.mark.parametrize("s_mask", [0b1011, 0b0001, 0b1111, 0b1010])
def test_noiseless_circuit_returns_the_secret_exactly(s_mask):
    n = 4
    target = target_string(n, s_mask)
    shots = measure_shots(n, s_mask, None, shots=64, seed=3)
    assert set(shots) == {target}          # a perfect delta, every shot


def test_zero_secret_gives_all_zeros():
    n = 5
    shots = measure_shots(n, 0, None, shots=32, seed=1)
    assert set(shots) == {"0" * n}


def test_noise_hurts_whole_strings_more_than_single_bits():
    """The claim of section 6: per-bit accuracy stays high while the
    all-n-bits-at-once rate decays."""
    n, s_mask = 8, 0b10110101
    target = target_string(n, s_mask)
    noise = MachineNoise.from_catalog("ibm-heron-r2")
    shots = measure_shots(n, s_mask, noise, shots=200, seed=5)
    per_bit = per_bit_rate(shots, target)
    whole = exact_rate(shots, target)
    assert per_bit > 0.95                  # each bit is usually fine
    assert whole < per_bit                 # but all of them at once is not
    # and the decay is roughly per_bit ** n (independent readout errors)
    assert abs(whole - per_bit ** n) < 0.12


def test_majority_vote_repairs_the_secret():
    n, s_mask = 8, 0b10110101
    target = target_string(n, s_mask)
    for mid in ("ibm-heron-r2", "rigetti-ankaa-3"):
        noise = MachineNoise.from_catalog(mid)
        shots = measure_shots(n, s_mask, noise, shots=25, seed=9)
        assert majority_vote(shots) == target


def test_target_string_matches_qsim_bit_order():
    # qsim is big-endian: qubit 0 is the leading character
    assert target_string(4, 0b0001) == "1000"
    assert target_string(4, 0b1000) == "0001"


# ---- the widgets' physics ------------------------------------------

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


@pytest.mark.parametrize("s", [0b10110, 0b00001, 0b11111, 0b01010])
def test_spectrum_widget_puts_all_mass_on_the_secret(s):
    """The 'spectrum' widget claims a single spike standing on s."""
    n, N = 5, 32
    a = [0.0] * N
    for x in range(N):
        par = 0
        for k in range(n):
            par ^= ((x >> k) & 1) & ((s >> k) & 1)
        a[x] = (-1.0 if par else 1.0) / math.sqrt(N)
    out = _walsh(a)
    peak = max(range(N), key=lambda i: abs(out[i]))
    assert peak == s
    assert np.isclose(out[peak] ** 2, 1.0, atol=1e-12)
    assert np.isclose(sum(v * v for i, v in enumerate(out) if i != peak),
                      0.0, atol=1e-12)


def test_orthogonality_widget_sums_to_2n_or_exactly_zero():
    """The 'orthogonality' widget claims 2^n on a match, 0 otherwise."""
    n, N = 4, 16
    for d in range(N):
        total = 0
        for x in range(N):
            par = 0
            for k in range(n):
                par ^= ((d >> k) & 1) & ((x >> k) & 1)
            total += -1 if par else 1
        assert total == (N if d == 0 else 0)


def test_bvmask_widget_computes_the_dot_product():
    """The 'bvmask' widget claims f(x) = parity of (s AND x)."""
    for s in range(32):
        for x in range(32):
            expected = bin(s & x).count("1") & 1
            kept = sum(((s >> i) & 1) & ((x >> i) & 1) for i in range(5))
            assert (kept & 1) == expected
