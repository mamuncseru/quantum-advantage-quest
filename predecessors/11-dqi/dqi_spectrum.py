"""DQI's mechanism, computed: from an objective to a code to a semicircle.

The autopsy asserts three things and asks you to verify them at proof level.
This file verifies them by computation instead, which is faster and harder
to fool:

  1. **The Fourier support of P(f) is the set of low-weight codewords.**
     For max-XORSAT the objective's sign function is s(x) = sum_i
     (-1)^(b_i + a_i . x), so a degree-l polynomial of it expands into
     characters at XOR-combinations of at most l constraint vectors. The
     spectrum is computed directly and compared against that set.

  2. **The achievable objective is the top eigenvalue of a tridiagonal
     matrix.** Restricting the state to error patterns of weight <= l makes
     the expected objective a quadratic form in the weights w_k, and the
     form is tridiagonal because s moves weight by one. Maximising it is an
     eigenvalue problem — no asymptotics needed.

  3. **That eigenvalue follows a semicircle.** lambda_max / m converges to
     2 sqrt(d(1-d)) with d = l/m, so the satisfied fraction is
     1/2 + sqrt(d(1-d)). Measured against the exact eigenvalue below.

The architecture, in one line: **optimisation -> coding theory -> borrow the
decoder**, and the decoding radius l is the only knob.

Run:  .venv/bin/python predecessors/11-dqi/dqi_spectrum.py
"""

from __future__ import annotations

from itertools import combinations

import numpy as np


# ------------------------------------------------------ the instance ------

def random_instance(n, m, rng):
    """A max-XORSAT instance: m constraints a_i . x = b_i over F_2.

    Rows are the constraint vectors, stored as Python ints so XOR is one
    operation and n is not capped at 63 bits (numpy's integers() overflows
    there, which is a silent trap when the same generator is reused for the
    larger instances the baseline needs).
    """
    nbytes = (n + 7) // 8
    mask = (1 << n) - 1
    A = []
    while len(A) < m:
        v = int.from_bytes(bytes(rng.integers(0, 256, size=nbytes,
                                              dtype=np.uint8)), "big") & mask
        if v:
            A.append(v)
    b = [int(v) for v in rng.integers(0, 2, size=m)]
    return A, b


def satisfied_count(A, b, x):
    """f(x) = how many constraints x satisfies."""
    return sum(1 for a, bb in zip(A, b)
               if (bin(a & x).count("1") & 1) == bb)


def objective_sign(A, b, n):
    """s(x) = 2 f(x) - m, as a vector over all 2^n assignments.

    s(x) = sum_i (-1)^(b_i + a_i . x): a sum of m characters. That is the
    whole reason a code appears — the objective *is* a Fourier-sparse
    function, supported on the constraint vectors themselves.
    """
    N = 1 << n
    xs = np.arange(N)
    s = np.zeros(N)
    for a, bb in zip(A, b):
        par = np.array([bin(a & int(x)).count("1") & 1 for x in xs])
        s += np.where(par == bb, 1.0, -1.0)
    return s


# --------------------------------------------------- the Fourier support ---

def walsh(vec):
    """Fast Walsh-Hadamard transform, 1/sqrt(2) per level (unitary)."""
    a = np.array(vec, dtype=float)
    N = a.size
    step = 1
    while step < N:
        for i in range(0, N, step << 1):
            u = a[i:i + step].copy()
            v = a[i + step:i + 2 * step].copy()
            a[i:i + step] = (u + v) / np.sqrt(2.0)
            a[i + step:i + 2 * step] = (u - v) / np.sqrt(2.0)
        step <<= 1
    return a


def reachable_frequencies(A, ell):
    """{ XOR of at most `ell` constraint vectors } — where the spectrum lives.

    In coding language: the images B^T y of error patterns y with weight at
    most ell. The decoder's job is to recover y from that image, which is
    syndrome decoding, which is why a decoding radius buys a polynomial
    degree.
    """
    out = {0}
    for k in range(1, ell + 1):
        for S in combinations(range(len(A)), k):
            v = 0
            for i in S:
                v ^= A[i]
            out.add(v)
    return out


def spectrum_support(vec, tol=1e-9):
    return {int(z) for z in np.flatnonzero(np.abs(walsh(vec)) > tol)}


def polynomial_of_objective(s, coeffs):
    """P(s) evaluated pointwise, for P given by its coefficients."""
    out = np.zeros_like(s)
    for c in reversed(coeffs):
        out = out * s + c
    return out


# ------------------------------------- the achievable objective, exactly ---

def tridiagonal_form(m, ell):
    """The matrix whose top eigenvalue is the best achievable <s>.

    Restrict the state to error patterns of weight <= ell and write it as
    sum_k w_k |D_k>, with |D_k> the uniform superposition over weight-k
    patterns. The objective s moves weight by exactly one, so <D_k| s |D_j>
    vanishes unless |k - j| = 1, and the coupling is

        <D_k| s |D_(k+1)> = sqrt((k+1)(m-k)) .

    Hence <s> = w^T T w and the best achievable value is lambda_max(T).

    VALIDITY, and it matters: this reduction treats the weight-k subspaces
    as orthogonal, which holds while the low-weight error patterns are
    distinguishable — i.e. below the code's distance. Past d = l/m ~ 1/2 the
    model stops describing anything real, and its lambda_max drifts up
    toward m, which would say "unlimited decoding radius solves the problem
    exactly". It does not; that is the model leaving its regime, and
    `semicircle_regime` marks the boundary.
    """
    T = np.zeros((ell + 1, ell + 1))
    for k in range(ell):
        T[k, k + 1] = T[k + 1, k] = np.sqrt((k + 1) * (m - k))
    return T


def best_objective(m, ell):
    """lambda_max of the tridiagonal form: the largest <s> a degree-ell
    DQI state can reach."""
    return float(np.linalg.eigvalsh(tridiagonal_form(m, ell))[-1])


def optimal_weights(m, ell):
    """The w_k achieving it — the amplitudes DQI actually prepares."""
    vals, vecs = np.linalg.eigh(tridiagonal_form(m, ell))
    w = vecs[:, -1]
    return w * np.sign(w[np.argmax(np.abs(w))])


def satisfied_fraction(m, ell):
    """<f>/m = 1/2 + <s>/(2m) — what the algorithm actually delivers."""
    return 0.5 + best_objective(m, ell) / (2 * m)


def semicircle_prediction(d):
    """The asymptotic law: 1/2 + sqrt(d(1-d)) with d = ell/m.

    Not quoted from the paper — compared against `satisfied_fraction` below,
    which is computed from an eigenvalue at finite m.
    """
    return 0.5 + np.sqrt(d * (1 - d))


def semicircle_regime(m):
    """Largest radius the tridiagonal model is trusted for: d <= 1/2."""
    return m // 2


def best_over_all_radii(m):
    """The radius maximising the fraction, within the model's regime.

    The semicircle peaks at d = 1/2, so a decoder reaching half the
    constraints extracts the most DQI can offer on this family. Searching
    past that would report a spurious optimum — see `tridiagonal_form`.
    """
    fracs = [(satisfied_fraction(m, l), l)
             for l in range(1, semicircle_regime(m) + 1)]
    return max(fracs)


def semicircle_convergence(ms=(50, 100, 400, 1600), d=0.25):
    """How fast the exact eigenvalue approaches the asymptotic law.

    The semicircle is a large-m statement, so the honest check is that the
    gap shrinks with m rather than that it is small at one m.
    """
    out = []
    for m in ms:
        ell = max(1, int(round(d * m)))
        out.append((m, satisfied_fraction(m, ell), semicircle_prediction(d)))
    return out


# ----------------------------------------------------------------- demo ----

def _demo():
    rng = np.random.default_rng(4)

    print("1 · THE FOURIER SUPPORT IS THE SET OF LOW-WEIGHT CODEWORDS\n")
    n, m = 10, 6
    A, b = random_instance(n, m, rng)
    s = objective_sign(A, b, n)
    print(f"   n = {n} variables, m = {m} constraints\n")
    print(f"   {'degree ℓ':>10} {'spectrum support':>18} "
          f"{'XORs of ≤ ℓ rows':>20} {'support ⊆ reachable':>22}")
    for ell in (1, 2, 3, 4):
        P = polynomial_of_objective(s, [0] * ell + [1])       # P(s) = s^ell
        sup = spectrum_support(P)
        reach = reachable_frequencies(A, ell)
        print(f"   {ell:>10} {len(sup):>18} {len(reach):>20} "
              f"{str(sup <= reach):>22}")
    print("\n   A degree-ℓ polynomial of the objective has ALL its Fourier")
    print("   weight on XOR-combinations of at most ℓ constraint vectors —")
    print("   i.e. on the low-weight words of the code the constraints")
    print("   generate. That is the whole reduction: an optimisation problem")
    print("   has become a coding problem, and the state can be built on the")
    print("   Fourier side and uncomputed with a DECODER.\n")

    print("2 · WHAT A DECODING RADIUS BUYS, EXACTLY\n")
    m2 = 400
    print(f"   m = {m2} constraints. Best achievable satisfied fraction:\n")
    print(f"   {'ℓ':>6} {'d = ℓ/m':>9} {'exact (eigenvalue)':>20} "
          f"{'semicircle law':>17} {'difference':>12}")
    for ell in (10, 40, 100, 200):
        d = ell / m2
        ex = satisfied_fraction(m2, ell)
        sc = semicircle_prediction(d)
        print(f"   {ell:>6} {d:>9.3f} {ex:>20.5f} {sc:>17.5f} "
              f"{abs(ex - sc):>12.5f}")
    frac, best_l = best_over_all_radii(m2)
    print(f"\n   peaks at ℓ = {best_l} (d = {best_l / m2:.2f}) with fraction "
          f"{frac:.4f} — the semicircle's maximum.\n")
    print("   The gap to the asymptotic law is a finite-m effect, and it")
    print("   closes as m grows (d = 0.25 throughout):\n")
    print(f"   {'m':>8} {'exact':>12} {'semicircle':>13} {'difference':>12}")
    for m3, ex, sc in semicircle_convergence():
        print(f"   {m3:>8} {ex:>12.5f} {sc:>13.5f} {abs(ex - sc):>12.5f}")
    print("\n   So the law is real and the finite-size correction is")
    print("   positive-order in 1/m. What it means for the hunt: at any")
    print("   finite decoding radius the fraction is 1/2 + sqrt(d(1-d)),")
    print("   and **a better decoder is literally a better optimiser** —")
    print("   which is why DQI's fate is decided in coding theory, not in")
    print("   quantum mechanics.\n")

    print("3 · THE AMPLITUDES IT PREPARES\n")
    w = optimal_weights(200, 20)
    print("   optimal weights w_k over error-pattern weight k (m=200, ℓ=20):")
    print("   " + "  ".join(f"{v:+.2f}" for v in w[:11]) + "  …")
    print("\n   Not uniform, and not concentrated at the maximum radius: the")
    print("   algorithm spreads amplitude across weights in the pattern that")
    print("   maximises the quadratic form. Getting these weights right is")
    print("   what makes it DQI rather than 'prepare low-weight errors'.")


if __name__ == "__main__":
    _demo()
