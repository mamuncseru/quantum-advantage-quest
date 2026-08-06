"""Tests that pin every numeric claim made in deep dive 01.

The house rule for this repository is that prose does not get to assert
numbers. If `notes.md` says the leakage mass is 0.786, this file computes
0.786 and fails when it stops being true.
"""

import sys
from fractions import Fraction
from math import gcd, pi
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from fourier_lab import (annihilator, annihilator_basis, character,
                         character_z2n, classical_mean_samples,
                         collision_entropy, convergents, corrupted_linear,
                         coset_state, dft_matrix, fourier_sample_support,
                         gf2_rank, gram, hadamard_matrix, kron_hadamard,
                         mean_of_signs, peak_mass, period_readout, popcount,
                         qft_circuit_matrix, qft_gate_count, recover_period,
                         samples_to_span, shift_eigenvalue, shift_matrix,
                         shor_success_rate, sign_vector, spectrum,
                         spike_height, subgroup_from_generators,
                         support_size, walsh_hadamard, xor_shift_matrix)


# --------------------------------------------------------- characters ------

@pytest.mark.parametrize("N", [2, 3, 4, 5, 8, 12])
def test_characters_are_orthonormal(N):
    G = gram([character(N, k) for k in range(N)])
    assert np.abs(G - np.eye(N)).max() < 1e-12


@pytest.mark.parametrize("N", [2, 3, 4, 5, 8, 16])
def test_dft_is_unitary(N):
    F = dft_matrix(N)
    assert np.abs(F.conj().T @ F - np.eye(N)).max() < 1e-12


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_hadamard_layer_is_the_z2n_character_table(n):
    """The claim of section 3: H^(x)n is not *like* a Fourier transform, it is
    the character table of Z_2^n, entry for entry."""
    assert np.abs(hadamard_matrix(n) - kron_hadamard(n)).max() < 1e-12


@pytest.mark.parametrize("n,z", [(3, 5), (4, 9), (5, 21)])
def test_z2n_characters_are_multiplicative(n, z):
    chi = character_z2n(n, z)
    N = 1 << n
    for x in range(N):
        for y in range(0, N, 3):
            assert chi[x ^ y] == pytest.approx(chi[x] * chi[y])


# ------------------------------------------------------------- shift -------

@pytest.mark.parametrize("N,k,a", [(8, 5, 3), (12, 1, 7), (16, 11, 5)])
def test_characters_are_shift_eigenvectors(N, k, a):
    chi = character(N, k)
    lhs = shift_matrix(N, a) @ chi
    assert np.abs(lhs - shift_eigenvalue(N, k, a) * chi).max() < 1e-12


def test_a_delta_is_not_a_shift_eigenvector():
    """The contrast that makes the point: shift a character and only a phase
    changes; shift anything localised and it moves."""
    N, delta = 8, np.zeros(8, dtype=complex)
    delta[3] = 1.0
    moved = shift_matrix(N, 2) @ delta
    assert np.abs(moved - delta).max() > 0.5          # genuinely different
    overlap = np.abs(np.vdot(delta, moved))
    assert overlap < 1e-12                            # not even parallel


def test_shifts_commute():
    N = 12
    A, B = shift_matrix(N, 5), shift_matrix(N, 7)
    assert np.abs(A @ B - B @ A).max() < 1e-12


@pytest.mark.parametrize("n,z,a", [(3, 5, 6), (4, 9, 3)])
def test_xor_shift_eigenvalue_is_the_character_value(n, z, a):
    chi = character_z2n(n, z)
    lhs = xor_shift_matrix(n, a) @ chi
    assert np.abs(lhs - chi[a] * chi).max() < 1e-12


# ------------------------------------------------ transform identities -----

@pytest.mark.parametrize("n", [1, 2, 3, 6, 8])
def test_fast_transform_equals_the_matrix(n):
    rng = np.random.default_rng(n)
    v = rng.normal(size=1 << n)
    assert np.abs(walsh_hadamard(v) - hadamard_matrix(n) @ v).max() < 1e-11


@pytest.mark.parametrize("n", [4, 6, 8])
def test_parseval(n):
    rng = np.random.default_rng(n + 100)
    v = rng.normal(size=1 << n)
    assert walsh_hadamard(v) @ walsh_hadamard(v) == pytest.approx(v @ v)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_convolution_theorem_over_z2n(n):
    """XOR-convolution becomes pointwise multiplication: the algebraic reason
    the Fourier basis is the right one for group structure."""
    N = 1 << n
    rng = np.random.default_rng(n + 7)
    f, g = rng.normal(size=N), rng.normal(size=N)
    conv = np.array([sum(f[y] * g[x ^ y] for y in range(N)) for x in range(N)])
    lhs = walsh_hadamard(conv)
    rhs = np.sqrt(N) * walsh_hadamard(f) * walsh_hadamard(g)
    assert np.abs(lhs - rhs).max() < 1e-10


# ------------------------------------------------- what the spectra say ----

@pytest.mark.parametrize("n", [3, 5, 7])
def test_frequency_zero_is_the_mean(n):
    rng = np.random.default_rng(n)
    bits = rng.integers(0, 2, size=1 << n)
    f = lambda x: int(bits[x])                                   # noqa: E731
    assert spectrum(f, n)[0] == pytest.approx(mean_of_signs(f, n))


@pytest.mark.parametrize("n", [4, 6])
def test_deutsch_jozsa_readout_is_exact(n):
    """Constant puts *all* the probability on frequency zero; balanced puts
    none there. One query, zero error — via Parseval, not luck."""
    for c in (0, 1):
        F = spectrum(lambda x: c, n)
        assert F[0] ** 2 == pytest.approx(1.0)
        assert support_size(F) == 1
    rng = np.random.default_rng(n)
    xs = rng.permutation(1 << n)
    half = set(int(v) for v in xs[:1 << (n - 1)])
    F = spectrum(lambda x: int(x in half), n)
    assert F[0] ** 2 == pytest.approx(0.0, abs=1e-24)


@pytest.mark.parametrize("n,s", [(4, 0b1011), (5, 0b10110), (8, 0b10110101)])
def test_bernstein_vazirani_is_one_spike(n, s):
    F = spectrum(lambda x: int(popcount(x & s)) & 1, n)
    assert support_size(F) == 1
    assert np.argmax(np.abs(F)) == s
    assert F[s] ** 2 == pytest.approx(1.0)


def test_a_random_function_has_no_readable_spectrum():
    """The negative half of the taxonomy in section 7: with no structure the
    spectrum is flat noise, and one sample carries essentially nothing."""
    n = 10
    rng = np.random.default_rng(3)
    bits = rng.integers(0, 2, size=1 << n)
    p = spectrum(lambda x: int(bits[x]), n) ** 2
    assert p.max() < 0.02                       # no usable peak
    assert collision_entropy(p) > n - 2.0       # nearly n bits of entropy


def test_collision_entropy_endpoints():
    n = 6
    delta = np.zeros(1 << n)
    delta[11] = 1.0
    assert collision_entropy(delta) == pytest.approx(0.0)
    flat = np.full(1 << n, 1.0 / (1 << n))
    assert collision_entropy(flat) == pytest.approx(n)


# ------------------------------------------- coset states / annihilator ----

@pytest.mark.parametrize("n,gens", [
    (3, [0b101]),
    (4, [0b1010]),
    (4, [0b1100, 0b0011]),
    (5, [0b10110]),
    (5, [0b10000, 0b01001]),
])
def test_annihilator_theorem(n, gens):
    """Section 8: Fourier-transform a coset state and the support is *exactly*
    the annihilator — for every offset, with no approximation."""
    H = subgroup_from_generators(gens, n)
    Hperp = annihilator(H, n)
    assert len(H) * len(Hperp) == 1 << n              # |H| |H-perp| = |G|
    for x0 in range(1 << n):
        assert fourier_sample_support(x0, H, n) == Hperp


@pytest.mark.parametrize("n,gens", [(4, [0b1010]), (5, [0b10110])])
def test_coset_offset_only_moves_phases(n, gens):
    """Why Simon learns the period and never the offset: changing x0 changes
    the phases and leaves every probability alone."""
    H = subgroup_from_generators(gens, n)
    Hh = hadamard_matrix(n)
    base = np.abs(Hh @ coset_state(0, H, n)) ** 2
    for x0 in range(1 << n):
        p = np.abs(Hh @ coset_state(x0, H, n)) ** 2
        assert np.abs(p - base).max() < 1e-12


@pytest.mark.parametrize("n,s", [(4, 0b1011), (6, 0b101101), (8, 0b10010111)])
def test_annihilator_basis_is_a_basis(n, s):
    basis = annihilator_basis(s, n)
    assert len(basis) == n - 1
    assert gf2_rank(basis, n) == n - 1
    for v in basis:
        assert int(popcount(v & s)) % 2 == 0


@pytest.mark.parametrize("n", [6, 8, 10])
def test_simon_sample_count_is_n_plus_a_constant(n):
    """The mechanism's real cost: n - 1 equations plus a small constant of
    coupon-collector waste — never a power of two."""
    mean = samples_to_span(n, trials=400, seed=n)
    assert n - 1 <= mean <= n + 2


# ------------------------------------------------------------- the QFT -----

@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_qft_circuit_equals_the_dft_matrix(n):
    """H, controlled phases and a bit reversal — O(n^2) gates — reproduce the
    full 2^n-point transform exactly."""
    assert np.abs(qft_circuit_matrix(n) - dft_matrix(1 << n)).max() < 1e-12


def test_qft_gate_count():
    assert [qft_gate_count(n) for n in (2, 3, 4, 10)] == [4, 7, 12, 60]


# ------------------------------------------------------ period finding -----

@pytest.mark.parametrize("N,r", [(64, 8), (256, 16), (128, 4)])
def test_exact_comb_when_the_period_divides(N, r):
    p = period_readout(N, r)
    hits = np.flatnonzero(p > 1e-12)
    assert list(hits) == [j * (N // r) for j in range(r)]
    assert np.allclose(p[hits], 1.0 / r)
    assert peak_mass(N, r) == pytest.approx(1.0)


@pytest.mark.parametrize("N,r", [(256, 5), (256, 7), (256, 11), (512, 13)])
def test_leakage_stays_above_the_textbook_floor(N, r):
    """A period that does not divide N smears the comb into a Dirichlet
    kernel. The classic bound says at least 4/pi^2 of the mass stays within
    half a bin of an exact peak; measured values are about 0.78."""
    m = peak_mass(N, r)
    assert m >= 4.0 / pi ** 2
    assert 0.75 < m < 0.82


def test_leakage_numbers_quoted_in_the_notes():
    assert peak_mass(256, 5) == pytest.approx(0.786, abs=5e-4)
    assert peak_mass(256, 7) == pytest.approx(0.781, abs=5e-4)


@pytest.mark.parametrize("x,denom", [(Fraction(3, 8), 8), (Fraction(5, 13), 13),
                                     (Fraction(21, 55), 55)])
def test_convergents_reach_the_exact_fraction(x, denom):
    """Legendre's theorem is what turns 'a multiple of N/r' into r."""
    assert (x.numerator, x.denominator) in convergents(x, denom)


@pytest.mark.parametrize("N,r", [(256, 5), (256, 7), (256, 11), (1024, 13)])
def test_legendre_guarantee_holds_inside_its_window(N, r):
    """Legendre: |x - p/q| < 1/(2q^2) forces p/q to be a convergent. So every
    outcome within half a bin of a peak decodes to r *provided* 2r^2 <= N —
    which is precisely why Shor's first register is twice as wide as the
    number being factored."""
    assert 2 * r * r <= N
    r_max = int(np.sqrt(N))
    for j in range(1, r):
        if gcd(j, r) != 1:
            continue
        for c in (int(np.floor(j * N / r)), int(np.ceil(j * N / r))):
            if abs(c - j * N / r) <= 0.5:
                assert recover_period(c, N, r_max) == r


def test_convergents_are_not_best_bounded_approximations():
    """Honest limitation of the textbook routine: 15/256's convergents leap
    straight past the denominator bound, so it reports nothing even though
    1/16 is the closest fraction with q <= 16. Outside the Legendre window
    the method has no guarantee — and that is the whole reason for the
    window."""
    assert recover_period(15, 256, 16) is None
    assert Fraction(15, 256).limit_denominator(16) == Fraction(1, 16)


def test_first_convergent_is_the_beginner_bug():
    """3/8's first non-trivial convergent is 1/2. Taking it would report a
    period of 2 for a function of period 8."""
    assert convergents(Fraction(3, 8), 8)[1] == (1, 2)
    assert recover_period(96, 256, 16) == 8       # 96/256 = 3/8


@pytest.mark.parametrize("N,r", [(256, 8), (256, 16), (128, 4)])
def test_success_rate_is_the_coprime_fraction_when_r_divides(N, r):
    """When r | N there is no leakage at all, and the only way to fail is to
    draw a j sharing a factor with r. So the success rate is phi(r)/r —
    Shor's repetitions pay for arithmetic, not for approximation."""
    coprime = sum(1 for j in range(r) if gcd(j, r) == 1) / r
    assert shor_success_rate(N, r) == pytest.approx(coprime, abs=1e-9)


@pytest.mark.parametrize("N,r,want", [(256, 5, 0.762), (256, 7, 0.806),
                                      (256, 11, 0.815)])
def test_success_rate_numbers_quoted_in_the_notes(N, r, want):
    assert shor_success_rate(N, r) == pytest.approx(want, abs=2e-3)


# ---------------------------------------------------------- robustness -----

@pytest.mark.parametrize("eps", [0.0, 0.02, 0.05, 0.1, 0.2])
def test_spike_decays_like_one_minus_two_eps(eps):
    """Corrupt an eps fraction of a linear function's values and the spike
    drops to 1 - 2 eps, so the one-shot success probability drops to
    (1 - 2 eps)^2. Three standard deviations of slack, nothing more."""
    n, s = 10, 0b1011010110
    got = spike_height(n, s, eps, seed=7)
    sd = 2.0 * np.sqrt(max(eps * (1 - eps), 1e-12) / (1 << n))
    assert abs(got - (1 - 2 * eps)) <= 3 * sd + 1e-12


def test_corruption_spreads_mass_off_the_spike():
    n, s = 10, 0b1011010110
    f = corrupted_linear(n, s, 0.1, seed=7)
    p = spectrum(f, n) ** 2
    assert p[s] < 0.65                      # the spike has lost a third
    assert support_size(p, tol=1e-9) > 900  # and the rest is smeared over 2^n


def test_the_classical_baseline_that_kills_deutsch_jozsa():
    """43 samples decide the promise with failure probability 1e-9, at every
    n. This is the number that makes DJ's exponential separation a
    statement about determinism, not about difficulty."""
    assert classical_mean_samples(1.0, 1e-9) == 43
    assert classical_mean_samples(1.0, 1e-9) == classical_mean_samples(1.0, 1e-9)


def test_sign_vector_is_a_unit_vector():
    for n in (2, 5, 8):
        v = sign_vector(lambda x: (x * x + 1) % 2, n)
        assert v @ v == pytest.approx(1.0)
