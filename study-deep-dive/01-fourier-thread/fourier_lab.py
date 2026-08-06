"""The Fourier mechanism, built from nothing and checked against itself.

Every numeric claim on `notes.md` is computed here and pinned by
`test_fourier_lab.py`. Nothing imports a signal-processing library: the
point of the deep dive is that the transform is a character table, so the
character table is what gets built.

Conventions
-----------
* A finite abelian group is either Z_N (integers mod N) or Z_2^n (bit
  strings under XOR). Elements of Z_2^n are Python ints in [0, 2^n).
* Transforms are the *unitary* normalisation, 1/sqrt(|G|), so that both
  directions are the same matrix up to conjugation and Parseval reads
  ||f||^2 = ||fhat||^2.
* Qubit ordering follows `qsim`: qubit 0 is the most significant bit of
  the flat amplitude index.

Run the demos:  .venv/bin/python study-deep-dive/01-fourier-thread/fourier_lab.py
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ------------------------------------------------------------- characters ---

def character(N, k):
    """The k-th character of Z_N as a vector: chi_k(x) = exp(2 pi i k x / N).

    A character is a homomorphism from the group to the unit circle:
    chi(x + y) = chi(x) chi(y). On Z_N every one of them has this form, and
    there are exactly N of them, indexed by k. That count is not an
    accident — a finite abelian group has exactly as many characters as
    elements, which is why the transform is square.
    """
    x = np.arange(N)
    return np.exp(2j * np.pi * k * x / N)


def dft_matrix(N):
    """Unitary Fourier transform on Z_N: rows are the normalised characters.

    F[k, x] = chi_k(x) / sqrt(N). Nothing else. The "Fourier transform" of
    a function is its expansion in this basis, and the basis is the
    character table of the group.
    """
    x = np.arange(N)
    return np.exp(2j * np.pi * np.outer(x, x) / N) / np.sqrt(N)


def character_z2n(n, z):
    """The z-th character of Z_2^n: chi_z(x) = (-1)^(x . z), the parity of x & z.

    The unit circle has only two rational points of order 2, so on Z_2^n
    every character is real and every "phase" is a sign. This is exactly
    why the Hadamard layer needs no rotation gates.
    """
    x = np.arange(1 << n)
    return np.where(popcount(x & z) & 1, -1.0, 1.0)


def hadamard_matrix(n):
    """H^(tensor n) built as the character table of Z_2^n.

    Built from the definition, *not* from a Kronecker product of H — so a
    test comparing it against the Kronecker product is a real check that
    the Hadamard layer is the Fourier transform on Z_2^n.
    """
    N = 1 << n
    x = np.arange(N)
    signs = np.where(popcount(x[:, None] & x[None, :]) & 1, -1.0, 1.0)
    return signs / np.sqrt(N)


def kron_hadamard(n):
    """The same matrix the machine actually applies: H tensor H tensor ..."""
    H = np.array([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2.0)
    M = np.array([[1.0]])
    for _ in range(n):
        M = np.kron(M, H)
    return M


def popcount(x):
    """Bit count, vectorised over numpy integer arrays."""
    x = np.asarray(x, dtype=np.int64)
    c = np.zeros_like(x)
    for b in range(64):
        if not np.any(x >> b):
            break
        c = c + ((x >> b) & 1)
    return c


def gram(vectors):
    """Matrix of normalised inner products <v_i, v_j> / len — the orthogonality
    check. For a set of distinct characters this is the identity."""
    V = np.asarray(vectors, dtype=complex)
    return V.conj() @ V.T / V.shape[1]


# ------------------------------------------------------------------ shift ---

def shift_matrix(N, a):
    """The shift operator S_a on functions over Z_N: (S_a f)(x) = f(x - a).

    Shifts commute with each other, so they are simultaneously
    diagonalisable, and their common eigenbasis is the Fourier basis. That
    sentence is the whole reason the Fourier transform exists.
    """
    S = np.zeros((N, N), dtype=complex)
    for x in range(N):
        S[x, (x - a) % N] = 1.0
    return S


def xor_shift_matrix(n, a):
    """The Z_2^n shift: (S_a f)(x) = f(x XOR a). Same story, XOR instead of +."""
    N = 1 << n
    S = np.zeros((N, N), dtype=complex)
    for x in range(N):
        S[x, x ^ a] = 1.0
    return S


def shift_eigenvalue(N, k, a):
    """S_a chi_k = chi_k(a)^{-1} chi_k, so the eigenvalue is exp(-2 pi i k a / N).

    Shifting a character does not change its shape at all — it multiplies
    it by one number. Shifting anything else scrambles it. This is the
    property that makes hidden *periodicity* visible in this basis and
    invisible in every other.
    """
    return np.exp(-2j * np.pi * k * a / N)


# ------------------------------------------- Walsh-Hadamard transform (fast) --

def walsh_hadamard(vec):
    """In-place-style fast Walsh-Hadamard transform, 1/sqrt(2) per level.

    n = log2(len) levels, each touching every entry once: N log N numeric
    operations classically. The quantum circuit runs the *same* butterfly
    but spends one gate per level, because level k is exactly "H on qubit
    k" — the group factorises, so the transform factorises, so the circuit
    is n gates deep. See notes.md section 6 for why this is not an FFT
    speedup.
    """
    a = np.array(vec, dtype=float if np.isrealobj(vec) else complex)
    N = a.size
    if N & (N - 1):
        raise ValueError("length must be a power of two")
    step = 1
    while step < N:
        for i in range(0, N, step << 1):
            u = a[i:i + step].copy()
            v = a[i + step:i + 2 * step].copy()
            a[i:i + step] = (u + v) / np.sqrt(2.0)
            a[i + step:i + 2 * step] = (u - v) / np.sqrt(2.0)
        step <<= 1
    return a


def sign_vector(f, n):
    """The state the phase oracle leaves behind: (-1)^f(x) / sqrt(2^n)."""
    N = 1 << n
    return np.array([(-1.0) ** (f(x) & 1) for x in range(N)]) / np.sqrt(N)


def spectrum(f, n):
    """Fourier (Walsh) coefficients of (-1)^f — literally the amplitudes the
    Hadamard sandwich hands you, one per basis state.

    Fhat[z] = 2^-n sum_x (-1)^(f(x) + x.z). Measuring the register samples
    z with probability Fhat[z]^2.
    """
    return walsh_hadamard(sign_vector(f, n))


def mean_of_signs(f, n):
    """Frequency zero, computed the boring way: 1 - 2 * (fraction of ones).

    The zero-frequency coefficient of any function is its mean, so
    Deutsch-Jozsa's question ("constant or balanced?") was a question about
    a mean all along — which is what makes it statistically cheap.
    """
    N = 1 << n
    ones = sum(f(x) & 1 for x in range(N))
    return 1.0 - 2.0 * ones / N


def support_size(vec, tol=1e-12):
    """How many Fourier coefficients are non-zero — the sparsity of the spectrum."""
    return int(np.sum(np.abs(np.asarray(vec)) > tol))


def collision_entropy(probs):
    """-log2 sum p^2: the effective number of outcomes, in bits.

    A useful one-number summary of "is this spectrum readable?". Zero bits
    means one outcome carries everything (BV); n bits means the sample is
    uniform noise.
    """
    p = np.asarray(probs, dtype=float)
    return -np.log2(np.sum(p ** 2))


# ---------------------------------------------------- subgroups over GF(2) ---

def rref_gf2(rows, n):
    """Row-reduce a list of n-bit ints over GF(2); returns (pivots, rows)."""
    rows = [r for r in rows if r]
    pivots, out = [], []
    for bit in range(n - 1, -1, -1):
        pivot = None
        for r in rows:
            if (r >> bit) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows = [r ^ pivot if ((r >> bit) & 1 and r is not pivot) else r
                for r in rows if r is not pivot]
        out.append(pivot)
        pivots.append(bit)
    return pivots, out


def gf2_rank(rows, n):
    """Rank over GF(2) of a set of n-bit vectors — how many independent
    equations Simon's algorithm has collected so far."""
    return len(rref_gf2(list(rows), n)[0])


def subgroup_from_generators(gens, n):
    """Every XOR-combination of the generators: the subgroup H <= Z_2^n."""
    H = {0}
    for g in gens:
        H |= {h ^ g for h in H}
    return sorted(H)


def annihilator(H, n):
    """H-perp = {z : z . h = 0 mod 2 for all h in H} — the dual subgroup.

    The annihilator theorem (notes.md section 8): Fourier-transform a coset
    state x0 + H and the amplitude is supported *exactly* on H-perp,
    uniformly, with the offset x0 hiding harmlessly in the phases. So one
    measurement is one uniform sample from H-perp, and the offset is
    unobservable. Simon and Shor are this sentence over two different
    groups.
    """
    return sorted(z for z in range(1 << n)
                  if all(int(popcount(z & h)) % 2 == 0 for h in H))


def coset_state(x0, H, n):
    """Uniform superposition over the coset x0 + H, as an amplitude vector."""
    v = np.zeros(1 << n, dtype=complex)
    for h in H:
        v[x0 ^ h] = 1.0
    return v / np.linalg.norm(v)


def fourier_sample_support(x0, H, n, tol=1e-12):
    """Which z's can actually come out of a coset state, measured not asserted."""
    amps = hadamard_matrix(n) @ coset_state(x0, H, n)
    return sorted(int(z) for z in np.flatnonzero(np.abs(amps) > tol))


def simon_function(n, s):
    """A two-to-one f with f(x) = f(x XOR s): the canonical hidden-XOR-period
    function. Implemented as "the smaller of x and x XOR s", which is
    constant on cosets of {0, s} and distinct across them."""
    def f(x):
        return min(x, x ^ s)
    return f


# ------------------------------------------------------- QFT over Z_N = 2^n ---

def phase_gate(k):
    """The controlled-rotation angle of the QFT butterfly: diag(1, e^{2 pi i / 2^k}).

    These are the twiddle factors of Cooley-Tukey, drawn as gates. Over
    Z_2^n every twiddle factor was +-1 and the layer collapsed to plain
    Hadamards; over Z_N they survive, which is exactly the difference
    between autopsy 01 and autopsy 04.
    """
    return np.diag([1.0, np.exp(2j * np.pi / (2 ** k))]).astype(complex)


def qft_circuit_matrix(n):
    """Build the QFT on n qubits from H, controlled-phase, and SWAPs.

    Standard construction: on each qubit j, apply H then controlled-R_k
    from every less significant qubit, then reverse the register with
    SWAPs. The test that this equals `dft_matrix(2**n)` is the check that
    O(n^2) gates really do implement the full N-point transform.
    """
    from qsim import H, apply, controlled

    SWAP = np.array([[1, 0, 0, 0],
                     [0, 0, 1, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1]], dtype=complex)
    N = 1 << n
    cols = []
    for basis in range(N):
        psi = np.zeros((2,) * n, dtype=complex)
        psi[tuple((basis >> (n - 1 - q)) & 1 for q in range(n))] = 1.0
        for j in range(n):
            psi = apply(psi, H, [j])
            for k in range(2, n - j + 1):
                ctrl = j + k - 1
                psi = apply(psi, controlled(phase_gate(k)), [ctrl, j])
        for j in range(n // 2):
            psi = apply(psi, SWAP, [j, n - 1 - j])
        cols.append(psi.reshape(-1))
    return np.array(cols).T


def qft_gate_count(n):
    """Gates in the construction above: n Hadamards + n(n-1)/2 rotations
    + floor(n/2) swaps."""
    return n + n * (n - 1) // 2 + n // 2


# ---------------------------------------------------------- period finding ---

def period_state(N, r, offset=0):
    """The first register after measuring the second in Shor: a comb of spikes
    at x = offset, offset + r, offset + 2r, ... below N."""
    xs = np.arange(offset, N, r)
    v = np.zeros(N, dtype=complex)
    v[xs] = 1.0
    return v / np.linalg.norm(v)


def period_readout(N, r, offset=0):
    """|QFT of the comb|^2 — the distribution Shor's measurement samples from.

    If r divides N the result is a perfect comb of r spikes at multiples of
    N/r. If it does not, the spikes smear into a Dirichlet kernel and the
    whole difficulty of Shor's analysis is bounding that smear.
    """
    amps = dft_matrix(N) @ period_state(N, r, offset)
    return np.abs(amps) ** 2


def peak_distance(N, r, c):
    """Circular distance from outcome c to the nearest multiple of N/r."""
    best = float("inf")
    for j in range(r):
        d = abs(c - j * N / r)
        best = min(best, d, N - d)
    return best


def peak_mass(N, r, offset=0, radius=0.5):
    """Probability of landing within `radius` of some exact multiple of N/r.

    The textbook floor is 4/pi^2 ~ 0.405 at radius 1/2 — that constant is
    the price of a period that does not divide N, and it is why Shor
    repeats the measurement.
    """
    probs = period_readout(N, r, offset)
    return float(sum(p for c, p in enumerate(probs)
                     if peak_distance(N, r, c) <= radius + 1e-12))


def convergents(x, max_denominator):
    """Continued-fraction convergents of x, denominators bounded.

    Legendre: if |x - p/q| < 1/(2 q^2) then p/q is a convergent of x. That
    theorem is the classical post-processing that turns "a multiple of N/r"
    into r, and it is the same Euclid-shaped tool the hunt's CRT work
    leans on.
    """
    out, frac = [], Fraction(x).limit_denominator(10 ** 12)
    a0 = frac.numerator // frac.denominator
    rem = frac - a0
    p_prev, q_prev, p, q = 1, 0, a0, 1
    if q <= max_denominator:
        out.append((p, q))
    while rem != 0:
        frac = 1 / rem
        a = frac.numerator // frac.denominator
        rem = frac - a
        p_prev, q_prev, p, q = p, q, a * p + p_prev, a * q + q_prev
        if q > max_denominator:
            break
        out.append((p, q))
    return out


def recover_period(measured, N, r_max):
    """Shor's classical tail: c/N -> continued fractions -> candidate r.

    Take the *deepest* convergent whose denominator still fits under
    r_max — the best rational approximation with a bounded denominator.
    Stopping at the first convergent with q > 1 is a classic beginner bug:
    3/8 has 1/2 as an early convergent, and 2 is not the period.
    """
    best = None
    for _, q in convergents(measured / N, r_max):
        if q > 1:
            best = q
    return best


def shor_success_rate(N, r, r_max=None, offset=0):
    """Exact probability that one measurement's convergent recovers r.

    Not sampled — every outcome is enumerated and weighted by its
    amplitude, so this number is a theorem about the distribution, not an
    experiment.
    """
    r_max = r_max or int(np.sqrt(N))
    probs = period_readout(N, r, offset)
    return float(sum(p for c, p in enumerate(probs)
                     if recover_period(c, N, r_max) == r))


# --------------------------------------------- robustness of a spike / mean ---

def corrupted_linear(n, s, eps, seed=0):
    """f(x) = s.x with an eps fraction of the values flipped at random.

    The spectrum of a *perfect* linear function is a single spike of height
    1. Corrupt it and the spike drops to about 1 - 2 eps, so the
    single-shot success probability falls to (1 - 2 eps)^2 — a
    second-order collapse that no amount of circuit cleverness repairs.
    This is what "the mechanism needs exact structure" costs, in numbers.
    """
    rng = np.random.default_rng(seed)
    N = 1 << n
    vals = np.array([int(popcount(x & s)) & 1 for x in range(N)])
    flip = rng.random(N) < eps
    vals = vals ^ flip.astype(int)
    return lambda x: int(vals[x])


def spike_height(n, s, eps, seed=0):
    """The surviving amplitude at frequency s after corrupting the function."""
    f = corrupted_linear(n, s, eps, seed=seed)
    return float(spectrum(f, n)[s])


def classical_mean_samples(gap, delta):
    """Hoeffding sample count to decide a mean is 0 vs +-1 within `gap`.

    2 ln(2/delta) / gap^2 samples of (-1)^f suffice, independent of n. Put
    gap = 1 and delta = 1e-9 and you get a couple of dozen — which is the
    number that kills Deutsch-Jozsa's headline separation, and it does not
    grow with the problem size at all.
    """
    return int(np.ceil(2.0 * np.log(2.0 / delta) / gap ** 2))


def annihilator_basis(s, n):
    """A basis of {z : z . s = 0} for a single hidden generator s != 0.

    Take the lowest set bit of s as the dependent coordinate; every other
    coordinate is free, and each free coordinate gives one basis vector
    (itself, plus the dependent bit when needed to keep the parity even).
    """
    piv = (s & -s).bit_length() - 1
    basis = []
    for b in range(n):
        if b == piv:
            continue
        v = 1 << b
        if (s >> b) & 1:
            v |= 1 << piv
        basis.append(v)
    return basis


def simon_sample(rng, s, n):
    """One Simon measurement: a uniformly random element of {0, s}-perp."""
    z = 0
    for v in annihilator_basis(s, n):
        if rng.integers(0, 2):
            z ^= v
    return z


def samples_to_span(n, s=None, seed=0, trials=2000):
    """Mean number of Simon samples needed to span the (n-1)-dim space H-perp.

    The coupon-collector cost of the hidden-subgroup mechanism: each
    measurement is one uniform vector from H-perp, and you need n - 1
    independent ones. Empirically n - 1 plus about 1.6 — a constant
    overhead, not a factor, and never a power of two.
    """
    rng = np.random.default_rng(seed)
    s = s if s is not None else (1 << (n - 1)) | 1
    total = 0
    for _ in range(trials):
        rows, draws = [], 0
        while gf2_rank(rows, n) < n - 1:
            rows.append(simon_sample(rng, s, n))
            draws += 1
            if draws > 500:
                break
        total += draws
    return total / trials


# ------------------------------------------------------------------- demos ---

def _demo():
    np.set_printoptions(precision=3, suppress=True)
    n = 5

    print("characters of Z_8 are orthonormal:  max off-diagonal =",
          f"{np.abs(gram([character(8, k) for k in range(8)]) - np.eye(8)).max():.2e}")

    print("H^(x)n is the Z_2^n character table: max |diff| =",
          f"{np.abs(hadamard_matrix(4) - kron_hadamard(4)).max():.2e}")

    S = shift_matrix(8, 3)
    chi = character(8, 5)
    print("shift eigenvalue check:", f"{np.abs(S @ chi - shift_eigenvalue(8, 5, 3) * chi).max():.2e}")

    print("\nspectra (n = %d):" % n)
    s = 0b10110
    for name, f in [("constant 0", lambda x: 0),
                    ("linear s.x", lambda x: int(popcount(x & s)) & 1),
                    ("balanced, not linear",
                     lambda x: ((x >> 4) & 1) ^ (((x >> 3) & 1) & ((x >> 2) & 1))),
                    ("AND (no promise)", lambda x: ((x >> 4) & (x >> 3)) & 1)]:
        F = spectrum(f, n)
        p = F ** 2
        print(f"  {name:22s} mean={F[0]:+.3f}  support={support_size(F):3d}"
              f"  max p={p.max():.3f}  entropy={collision_entropy(p):.2f} bits")

    print("\nQFT circuit vs DFT matrix (n=4): max |diff| =",
          f"{np.abs(qft_circuit_matrix(4) - dft_matrix(16)).max():.2e}",
          f" gates = {qft_gate_count(4)}")

    print("\nperiod finding, N = 256:")
    for r in (8, 16, 5, 7, 11):
        print(f"  r={r:3d}  divides N: {str(256 % r == 0):5s}"
              f"  mass within 1/2 bin = {peak_mass(256, r):.3f}"
              f"  one-shot recovery = {shor_success_rate(256, r):.3f}")

    print("\nSimon on n=6, s=0b101101: Fourier support == H-perp:",
          fourier_sample_support(0b011010, subgroup_from_generators([0b101101], 6), 6)
          == annihilator(subgroup_from_generators([0b101101], 6), 6))
    print("  mean samples to span H-perp (n=8):", f"{samples_to_span(8):.2f}",
          "vs n-1 =", 7)

    print("\nspike under corruption (n=10, s=0b1011010110):")
    for eps in (0.0, 0.02, 0.05, 0.1, 0.2):
        h = spike_height(10, 0b1011010110, eps, seed=7)
        print(f"  eps={eps:4.2f}  spike={h:+.3f}  p={h*h:.3f}"
              f"  theory (1-2eps)^2={(1-2*eps)**2:.3f}")

    print("\nclassical samples to decide the DJ promise (gap 1, delta 1e-9):",
          classical_mean_samples(1.0, 1e-9), "— independent of n")


if __name__ == "__main__":
    _demo()
