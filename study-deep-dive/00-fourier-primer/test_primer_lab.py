"""Tests pinning every number the prerequisite page quotes.

Two of these are worth more than the rest: `test_naive_dft_matches_the_deep_dive_matrix`
checks the primer's slow, hand-written transform against the matrix version
deep dive 01 actually uses, and `test_two_point_dft_is_the_hadamard_gate`
checks the sentence the whole primer exists to earn.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "01-fourier-thread"))

import numpy as np
import pytest

from primer_lab import (alias_frequency, aliases_to_same_samples,
                        amount_of_frequency, complex_wave, correlate, cosine,
                        gibbs_fraction, gibbs_overshoot, leakage_profile,
                        naive_dft, naive_idft, orthogonality_table, peak_share,
                        power_spectrum, sample_times, sine, square_series,
                        square_wave, sweep, two_point_dft, walsh_pattern)

from fourier_lab import dft_matrix, hadamard_matrix   # deep dive 01


# ------------------------------------------------------- waves & probes -----

@pytest.mark.parametrize("N", [8, 16, 64])
def test_distinct_frequencies_cancel(N):
    """The one computation: matched probes pile up, mismatched ones cancel."""
    for k in range(N // 2):
        for j in range(N // 2):
            got = correlate(complex_wave(N, k), complex_wave(N, j))
            assert abs(got - (1.0 if k == j else 0.0)) < 1e-12


def test_correlation_reads_off_amplitudes():
    """Build a signal from known ingredients; get the recipe back."""
    N = 128
    sig = 2.0 * cosine(N, 3) + 0.5 * cosine(N, 7) + 1.5
    assert abs(amount_of_frequency(sig, 0) - 1.5) < 1e-12
    assert abs(abs(amount_of_frequency(sig, 3)) - 1.0) < 1e-12   # 2.0 / 2
    assert abs(abs(amount_of_frequency(sig, 7)) - 0.25) < 1e-12  # 0.5 / 2
    for k in (1, 2, 4, 5, 6, 8, 9):
        assert abs(amount_of_frequency(sig, k)) < 1e-12


def test_a_real_cosine_splits_between_plus_and_minus_k():
    """Why a real cosine gives *half* its amplitude at +k: it is the average
    of the +k and -k complex waves, and both bins get a share."""
    N, k = 64, 5
    sig = cosine(N, k, amp=2.0)
    assert abs(abs(amount_of_frequency(sig, k)) - 1.0) < 1e-12
    assert abs(abs(amount_of_frequency(sig, N - k)) - 1.0) < 1e-12


def test_phase_is_the_argument_not_the_magnitude():
    """Shifting a wave in time leaves the magnitude alone and rotates the
    phase — the property that makes complex probes worth the trouble."""
    N, k = 64, 6
    a = amount_of_frequency(cosine(N, k), k)
    b = amount_of_frequency(cosine(N, k, phase=np.pi / 2), k)
    assert abs(abs(a) - abs(b)) < 1e-12
    assert abs(abs(np.angle(b) - np.angle(a)) - np.pi / 2) < 1e-12


def test_cosine_and_sine_are_orthogonal():
    N, k = 32, 5
    assert abs(correlate(cosine(N, k), sine(N, k))) < 1e-12


# ------------------------------------------------------ the transform -------

@pytest.mark.parametrize("N", [2, 4, 8, 16])
def test_naive_dft_matches_the_deep_dive_matrix(N):
    """The primer's explicit double loop and deep dive 01's character-table
    matrix are the same transform. Two implementations, one answer."""
    rng = np.random.default_rng(N)
    x = rng.normal(size=N) + 1j * rng.normal(size=N)
    assert np.abs(naive_dft(x) - dft_matrix(N).conj() @ x).max() < 1e-10


@pytest.mark.parametrize("N", [8, 32])
def test_round_trip(N):
    rng = np.random.default_rng(N + 1)
    x = rng.normal(size=N)
    assert np.abs(naive_idft(naive_dft(x)) - x).max() < 1e-10


@pytest.mark.parametrize("N", [8, 32])
def test_parseval_energy_is_conserved(N):
    rng = np.random.default_rng(N + 2)
    x = rng.normal(size=N)
    assert np.sum(np.abs(naive_dft(x)) ** 2) == pytest.approx(np.sum(x ** 2))


def test_sweep_is_the_transform_up_to_conjugation():
    N = 32
    rng = np.random.default_rng(5)
    x = rng.normal(size=N)
    assert np.abs(sweep(x) * np.sqrt(N) - naive_dft(x)).max() < 1e-10


def test_shifting_a_signal_only_moves_phases():
    """The classical ancestor of deep dive 01's annihilator theorem: a shift
    never changes the power spectrum."""
    N = 64
    rng = np.random.default_rng(9)
    x = rng.normal(size=N)
    for a in (1, 7, 31):
        assert np.abs(power_spectrum(np.roll(x, a)) -
                      power_spectrum(x)).max() < 1e-12


# ---------------------------------------------------- the Fourier series ----

def test_square_wave_harmonics():
    """Odd harmonics with amplitude 4/(pi k), even ones exactly zero —
    measured by correlation, not quoted from the formula."""
    N = 4096
    sq = square_wave(N)
    for k in range(1, 10):
        got = 2.0 * abs(amount_of_frequency(sq, k))
        want = 4.0 / (np.pi * k) if k % 2 else 0.0
        assert abs(got - want) < 2e-3


@pytest.mark.parametrize("terms,want", [(9, 0.0900), (49, 0.0895), (199, 0.0895)])
def test_gibbs_overshoot_never_goes_away(terms, want):
    """The 9% is the Wilbraham-Gibbs constant, 0.089490. More terms make the
    spike narrower, never shorter."""
    assert gibbs_fraction(terms) == pytest.approx(want, abs=5e-4)


def test_gibbs_converges_to_the_constant():
    assert gibbs_fraction(2001) == pytest.approx(0.0894898, abs=1e-4)


def test_more_terms_do_not_reduce_the_peak():
    peaks = [gibbs_overshoot(t) for t in (49, 199, 799)]
    assert max(peaks) - min(peaks) < 1e-3


# --------------------------------------------------------- sampling ---------

@pytest.mark.parametrize("N,k,alias", [(16, 1, 1), (16, 15, -1), (16, 17, 1),
                                       (16, 31, -1), (16, 8, 8)])
def test_alias_frequency(N, k, alias):
    assert alias_frequency(k, N) == alias


def test_aliased_frequencies_are_literally_the_same_samples():
    """N samples can tell apart exactly N frequencies. Beyond that a rising
    wave is indistinguishable from a falling one — the wagon-wheel effect."""
    assert aliases_to_same_samples(16, 1, 17)
    assert aliases_to_same_samples(16, 3, 19)
    assert aliases_to_same_samples(16, 15, 1)      # cos is even: k and -k agree
    assert not aliases_to_same_samples(16, 1, 2)


# ---------------------------------------------------------- leakage ---------

def test_an_exact_frequency_lands_in_one_bin():
    p = leakage_profile(64, 8.0)
    assert peak_share(64, 8.0) == pytest.approx(1.0, abs=1e-9)
    assert int(np.sum(p > 1e-12)) == 2          # +k and -k


@pytest.mark.parametrize("freq,want", [(8.5, 0.423), (8.25, 0.818)])
def test_a_fractional_frequency_smears(freq, want):
    """Nothing cancels perfectly any more, so the energy spreads over every
    bin. Same algebra as Shor's leaking comb, different vocabulary."""
    assert peak_share(64, freq) == pytest.approx(want, abs=2e-3)


def test_leakage_is_worst_exactly_halfway_between_bins():
    shares = [(d, peak_share(64, 8.0 + d)) for d in (0.0, 0.1, 0.25, 0.5)]
    assert shares == sorted(shares, key=lambda kv: -kv[1])


# ------------------------------------------------- the bridge to Z_2^n ------

def test_two_point_dft_is_the_hadamard_gate():
    """The sentence the primer exists to earn: run the same formula on a
    group with two elements and the Hadamard gate falls out."""
    assert np.abs(two_point_dft() - dft_matrix(2)).max() < 1e-12


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_walsh_patterns_are_the_z2n_transform(n):
    """Stack the sign patterns and you have deep dive 01's Hadamard layer."""
    W = np.array([walsh_pattern(n, z) for z in range(1 << n)]) / np.sqrt(1 << n)
    assert np.abs(np.abs(W) - np.abs(hadamard_matrix(n))).max() < 1e-12
    G = orthogonality_table([walsh_pattern(n, z) for z in range(1 << n)])
    assert np.abs(G - np.eye(1 << n)).max() < 1e-12


def test_the_alternating_pattern_is_the_top_frequency():
    """cos at frequency N/2 samples to +1, -1, +1, -1 — a "wave" whose only
    values are signs, and it is literally a Walsh pattern. That is what every
    wave looks like once the group has exponent two."""
    N, n = 16, 4
    assert np.abs(cosine(N, N // 2) - walsh_pattern(n, 1)).max() < 1e-12


def test_sample_times_are_a_full_period():
    assert sample_times(8)[0] == 0.0
    assert sample_times(8)[-1] == pytest.approx(7 / 8)
