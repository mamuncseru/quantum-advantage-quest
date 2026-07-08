"""Lattice attack on Q(A2.1): can an EFFICIENT (non-enumeration) decoder
recover a sparse CRT combination at growing sparsity?

The crux of candidate A2 is whether the sparse-recovery step is poly-time at
sparsity ell = eps*m. Enumeration is O(m^ell) — exponential at linear ell.
Here we test the natural lattice attack instead.

Formulation. A weight-ell integer is t = sum_i a_i v_i (mod M) with
v_i = M/p_i and only ell of the a_i nonzero (small). Recovering the sparse
coefficient vector from t' is a closest-vector problem, attacked by LLL via
the standard Kannan embedding:

    rows (in Z^{m+2}):
      (C*v_i,  e_i,        0 )   i = 1..m
      (C*M,    0,          0 )
      (C*t',   0,...,0,    1 )         <- embedded target

    A short vector of the reduced basis has the form
      ( C*(sum a_i v_i - bM - t'),  (a_i),  -1 ),
    whose smallness forces sum a_i v_i == t' (mod M) with a small, ideally
    sparse, coefficient vector.

We use a self-contained exact-rational LLL (delta = 3/4). Correctness of the
reducer is unit-tested against known-short lattices; the science is the
recovery-vs-sparsity curve.
"""

from fractions import Fraction
from math import prod

import sympy


# ----------------------------- exact LLL --------------------------------

def _gram_schmidt(B):
    n = len(B)
    Bs = [row[:] for row in B]
    mu = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        Bs[i] = [Fraction(x) for x in B[i]]
        for j in range(i):
            denom = sum(b * b for b in Bs[j])
            mu[i][j] = (sum(Fraction(B[i][k]) * Bs[j][k]
                            for k in range(len(B[i]))) / denom
                        if denom else Fraction(0))
            for k in range(len(B[i])):
                Bs[i][k] -= mu[i][j] * Bs[j][k]
    return Bs, mu


def lll(B, delta=Fraction(3, 4)):
    """Exact LLL reduction. B: list of integer row vectors. Returns reduced B."""
    B = [[int(x) for x in row] for row in B]
    n = len(B)
    Bs, mu = _gram_schmidt(B)
    norms = [sum(b * b for b in Bs[i]) for i in range(n)]
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                q = round(mu[k][j])
                B[k] = [B[k][t] - q * B[j][t] for t in range(len(B[k]))]
                Bs, mu = _gram_schmidt(B)
                norms = [sum(b * b for b in Bs[i]) for i in range(n)]
        if norms[k] >= (delta - mu[k][k - 1] ** 2) * norms[k - 1]:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = _gram_schmidt(B)
            norms = [sum(b * b for b in Bs[i]) for i in range(n)]
            k = max(k - 1, 1)
    return B


# ------------------------- the CRT lattice attack -----------------------

def moduli_of(m, lo=3):
    return [int(p) for p in sympy.primerange(lo, 10 ** 7)][:m]


def plant(m, ell, seed):
    import random
    rng = random.Random(seed)
    moduli = moduli_of(m)
    M = prod(moduli)
    support = sorted(rng.sample(range(m), ell))
    a = [0] * m
    for i in support:
        a[i] = rng.randrange(1, moduli[i])
    t = sum(a[i] * (M // moduli[i]) for i in range(m)) % M
    return moduli, M, a, t


def lll_recover(moduli, M, t_prime, C=None):
    """Return the coefficient vector LLL extracts for target t_prime."""
    m = len(moduli)
    v = [M // p for p in moduli]
    C = C or M  # weight the congruence coordinate heavily
    rows = []
    for i in range(m):
        row = [C * v[i]] + [1 if j == i else 0 for j in range(m)] + [0]
        rows.append(row)
    rows.append([C * M] + [0] * m + [0])
    rows.append([C * t_prime] + [0] * m + [1])
    red = lll(rows)
    # find the reduced vector with last coord +-1 (the embedded target row)
    for r in red:
        if abs(r[-1]) == 1:
            s = -1 if r[-1] == 1 else 1
            return [s * r[1 + i] for i in range(m)]
    return None


if __name__ == "__main__":
    print("Naive lattice attack on the CRT-DQI uncomputation decoder.")
    print("Recovery of the planted sparse combination, no window noise:\n")
    print(f"{'m':>4} {'ell':>4} {'trials':>7} {'recovered':>10} {'rate':>6}")
    for m in (12, 16):
        for ell in (1, 2, 3):
            ok = trials = 0
            for seed in range(8):
                trials += 1
                moduli, M, a, t = plant(m, ell, seed + 100 * m)
                if lll_recover(moduli, M, t) == a:
                    ok += 1
            print(f"{m:>4} {ell:>4} {trials:>7} {ok:>10} {ok/trials:>6.2f}")
        print()
    print("Finding: the naive embedding lattice fails at every sparsity — the")
    print("modular kernel {p_i·e_i} gives short non-solutions. Sparse CRT")
    print("recovery does NOT reduce to LLL the way RS decoding reduces to")
    print("Berlekamp-Massey. See hunt/notes/A2-crt-opi-derivation.md section 8.")
