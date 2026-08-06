"""Classical Fourier analysis, built from nothing, for the prerequisite page.

Deliberately the *slow* implementations: the transform here is an explicit
double loop over "correlate the signal with one probe wave", because that is
the sentence the primer is trying to make physical. A test checks this naive
version against the fast, matrix version used by deep dive 01 — two
independent implementations agreeing is worth more than one clever one.

Nothing here is quantum. That is the point: every idea on the primer page is
two hundred years old, and the quantum part of deep dive 01 is what happens
when you run these same formulas on amplitudes instead of numbers.

Run the demos:  .venv/bin/python study-deep-dive/00-fourier-primer/primer_lab.py
"""

from __future__ import annotations

import numpy as np

TWO_PI = 2.0 * np.pi


# ------------------------------------------------------------ waves ---------

def sample_times(N):
    """N evenly spaced sample points on one period, as fractions of it."""
    return np.arange(N) / N


def cosine(N, k, phase=0.0, amp=1.0):
    """amp * cos(2 pi k t + phase), sampled at N points over one period.

    k is the frequency in *cycles per period*: k = 3 means the wave goes
    up and down three times across the window. Everything in Fourier
    analysis is bookkeeping about these integers.
    """
    return amp * np.cos(TWO_PI * k * sample_times(N) + phase)


def sine(N, k, amp=1.0):
    return amp * np.sin(TWO_PI * k * sample_times(N))


def complex_wave(N, k):
    """exp(2 pi i k t): one object holding a cosine and a sine at once.

    The reason complex exponentials replace sin/cos everywhere: a shift in
    time becomes multiplication by a single number, exp(2 pi i k a), instead
    of a two-line trigonometric identity mixing sin into cos. That single
    number is what becomes the "character" of deep dive 01, and the "phase"
    of a qubit.
    """
    return np.exp(1j * TWO_PI * k * sample_times(N))


# --------------------------------------------------- correlation / projection

def correlate(signal, probe):
    """Average of signal * probe: "how much of the probe is in the signal".

    This is the only measurement in classical Fourier analysis. Multiply
    point by point, then average. If the two rise and fall together the
    products are mostly positive and the average is large; if they drift in
    and out of step the products cancel and the average is ~0.
    """
    signal = np.asarray(signal, dtype=complex)
    probe = np.asarray(probe, dtype=complex)
    return complex(np.mean(signal * np.conj(probe)))


def amount_of_frequency(signal, k):
    """The complex Fourier coefficient at frequency k: magnitude and phase.

    Magnitude answers "how much of this frequency is present", argument
    answers "shifted by how much". Both fall out of one correlation because
    the probe is complex.
    """
    N = len(signal)
    return correlate(signal, complex_wave(N, k))


def sweep(signal, kmax=None):
    """Correlation against every probe frequency: the spectrum, the slow way."""
    N = len(signal)
    kmax = N if kmax is None else kmax
    return np.array([amount_of_frequency(signal, k) for k in range(kmax)])


def naive_dft(signal):
    """The discrete Fourier transform written as N correlations, unitary scale.

    X[k] = (1/sqrt(N)) sum_x signal[x] exp(-2 pi i k x / N).

    Deliberately O(N^2) and written as an explicit loop. `test_primer_lab.py`
    checks it against the matrix built in deep dive 01, so the pedagogical
    version and the working version are pinned to each other.
    """
    x = np.asarray(signal, dtype=complex)
    N = x.size
    out = np.zeros(N, dtype=complex)
    for k in range(N):
        acc = 0.0 + 0.0j
        for t in range(N):
            acc += x[t] * np.exp(-1j * TWO_PI * k * t / N)
        out[k] = acc / np.sqrt(N)
    return out


def naive_idft(spectrum):
    """The inverse: same loop, opposite sign, same normalisation."""
    X = np.asarray(spectrum, dtype=complex)
    N = X.size
    out = np.zeros(N, dtype=complex)
    for t in range(N):
        acc = 0.0 + 0.0j
        for k in range(N):
            acc += X[k] * np.exp(1j * TWO_PI * k * t / N)
        out[t] = acc / np.sqrt(N)
    return out


def power_spectrum(signal):
    """|X[k]|^2 — the "how loud is each frequency" picture, and the thing a
    quantum measurement samples from in deep dive 01."""
    return np.abs(naive_dft(signal)) ** 2


# ---------------------------------------------------------- Fourier series --

def square_wave(N, duty=0.5):
    """+1 for the first `duty` of the period, -1 after: the standard test case."""
    t = sample_times(N)
    return np.where(t < duty, 1.0, -1.0)


def square_series(N, terms):
    """Partial sum of the square wave's Fourier series: (4/pi) sum sin(2 pi k t)/k
    over odd k, `terms` of them.

    The coefficients are 4/(pi k) for odd k and exactly zero for even k, and
    `test_square_wave_harmonics` checks that against the correlations rather
    than trusting the formula.
    """
    t = sample_times(N)
    out = np.zeros(N)
    for j in range(terms):
        k = 2 * j + 1
        out += (4.0 / (np.pi * k)) * np.sin(TWO_PI * k * t)
    return out


def gibbs_overshoot(terms, points=2000):
    """Peak value of the partial sum. The square wave's own peak is 1.

    Scanned on a fine grid *near the jump* rather than on the whole period:
    the overshoot lives within about 1/(2K) of the edge, where K is the
    highest harmonic, so a fixed grid over the full period stops resolving
    it once you pass a few hundred terms and silently reports a peak that is
    too low. That is a measurement artefact, not physics — and it is exactly
    the kind of thing this repository's "pin every number" rule exists to
    catch.
    """
    kmax = 2 * terms - 1
    t = np.linspace(0.0, 3.0 / (2 * kmax), points)
    ks = np.arange(1, kmax + 1, 2)
    vals = (4.0 / np.pi) * (np.sin(TWO_PI * np.outer(t, ks)) / ks).sum(axis=1)
    return float(vals.max())


def gibbs_fraction(terms, points=2000):
    """Overshoot as a fraction of the jump height (the jump here is 2).

    Converges to the Wilbraham-Gibbs constant 0.08949...: the partial sums
    overshoot a jump by about 9% of it forever, no matter how many terms you
    add. More terms make the spike narrower, never shorter. Worth meeting
    once, because it is the cleanest case of "a finite number of frequencies
    cannot represent a sharp edge" — which is leakage (see `leakage_profile`)
    seen from the other side, and the reason deep dive 01's section 8 has a
    Dirichlet kernel in it.
    """
    return (gibbs_overshoot(terms, points) - 1.0) / 2.0


# ------------------------------------------------------ sampling / aliasing --

def alias_frequency(k, N):
    """Which frequency a probe of index k is indistinguishable from.

    With N samples per period there are only N distinguishable frequencies:
    k and k + N give literally identical sample values. Above N/2 a rising
    frequency looks like a falling one — the wagon-wheel effect, and the
    reason a spectrum has a highest meaningful bin.
    """
    k = int(k) % N
    return k if k <= N // 2 else k - N


def aliases_to_same_samples(N, k1, k2, tol=1e-12):
    return bool(np.abs(cosine(N, k1) - cosine(N, k2)).max() < tol)


# ------------------------------------------------------------- leakage ------

def leakage_profile(N, freq):
    """Power spectrum of a pure tone at (possibly fractional) frequency `freq`.

    An exact integer frequency lands in one bin and every other correlation
    cancels perfectly. A fractional one cannot cancel anywhere, so its energy
    smears across all bins. This *is* the phenomenon that costs Shor's
    algorithm its exactness when the period does not divide N — same algebra,
    different name in each field.
    """
    t = sample_times(N)
    return power_spectrum(np.cos(TWO_PI * freq * t))


def peak_share(N, freq):
    """Fraction of the energy sitting in the two largest bins."""
    p = leakage_profile(N, freq)
    order = np.argsort(p)[::-1]
    return float(p[order[:2]].sum() / p.sum())


# ------------------------------------------- the bridge to Z_2^n ------------

def walsh_pattern(n, z):
    """(-1)^(x . z) for x = 0 .. 2^n - 1 — a "wave" with only two values.

    A character must send the group into the unit circle. If every element
    doubled is the identity (which is what XOR means), the only available
    values are +1 and -1. So on Z_2^n a wave *is* a sign pattern, and this
    function is the whole difference between the primer and deep dive 01.
    """
    N = 1 << n
    x = np.arange(N)
    bits = np.zeros(N, dtype=int)
    for b in range(n):
        bits += ((x >> b) & 1) * ((z >> b) & 1)
    return np.where(bits % 2, -1.0, 1.0)


def two_point_dft():
    """The DFT on N = 2 — which is the Hadamard gate, up to nothing at all."""
    return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def orthogonality_table(vectors):
    V = np.asarray(vectors, dtype=complex)
    return V.conj() @ V.T / V.shape[1]


# -------------------------------------------------------------- demos -------

def _demo():
    np.set_printoptions(precision=3, suppress=True)
    N = 64

    print("a signal is a list of numbers; a frequency is how many times it "
          "wiggles per window\n")
    sig = cosine(N, 3, amp=2.0) + cosine(N, 7, phase=1.1) + 0.5

    print("correlating that signal against each probe frequency:")
    for k in range(0, 9):
        c = amount_of_frequency(sig, k)
        bar = "#" * int(round(abs(c) * 20))
        print(f"  k = {k}:  |c| = {abs(c):.3f}  {bar}")
    print("  (only 0, 3 and 7 survive — everything else cancels)\n")

    print("naive DFT vs its own inverse: max round-trip error =",
          f"{np.abs(naive_idft(naive_dft(sig)) - sig).max():.2e}")
    print("Parseval — energy in time = energy in frequency:",
          f"{np.sum(np.abs(sig) ** 2):.6f} vs "
          f"{np.sum(np.abs(naive_dft(sig)) ** 2):.6f}\n")

    print("square wave, Fourier series partial sums (jump height 2):")
    for terms in (1, 3, 9, 49, 199):
        print(f"  {terms:3d} harmonics → peak {gibbs_overshoot(terms):.4f}"
              f"   overshoot {100 * gibbs_fraction(terms):.2f}% of the jump")
    print("  the 9% never goes away — that is the Gibbs phenomenon\n")

    print("aliasing with N = 16 samples:")
    for k in (1, 15, 17, 31):
        print(f"  probe k = {k:2d} is indistinguishable from k = "
              f"{alias_frequency(k, 16):+d}")
    print()

    print("leakage — a tone that does not fit a whole number of cycles:")
    for freq in (8.0, 8.5, 8.25):
        print(f"  freq = {freq:4.2f}:  two-bin share of the energy = "
              f"{peak_share(64, freq):.3f}")
    print()

    print("the bridge: on Z_2 the only wave values are +-1, and the "
          "2-point DFT is")
    print(two_point_dft().real, " — the Hadamard gate")
    G = orthogonality_table([walsh_pattern(3, z) for z in range(8)])
    print("8 Walsh patterns, orthogonality table is the identity:",
          f"max off-diagonal {np.abs(G - np.eye(8)).max():.1e}")


if __name__ == "__main__":
    _demo()
