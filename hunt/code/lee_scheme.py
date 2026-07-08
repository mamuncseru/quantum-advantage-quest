"""Lee kill-check: does the Lee metric on Z_q^n give a P-polynomial
translation association scheme?

DQI's analysis (Hamming: Krawtchouk; rank: q-Krawtchouk, arXiv 2606.04843)
needs a P-POLYNOMIAL scheme: the distance-1 operator A_1 must generate the
whole Bose-Mesner algebra, so the radial dynamics reduce to a (D+1)x(D+1)
tridiagonal Jacobi matrix — "one amplitude per shell." Necessary condition:
A_1 has exactly D+1 distinct eigenvalues, D = n*floor(q/2) the Lee diameter.

We COMPUTE this rather than assume it. We also directly test the association-
scheme property (constant intersection numbers), so no structure is taken on
faith.

Run: .venv/bin/python hunt/code/lee_scheme.py
"""

from itertools import product

import numpy as np


def lee_coord(a, q):
    a %= q
    return min(a, q - a)


def lee_weight(x, q):
    return sum(lee_coord(xi, q) for xi in x)


def distance_matrices(q, n):
    elems = list(product(range(q), repeat=n))
    idx = {e: i for i, e in enumerate(elems)}
    N, D = len(elems), n * (q // 2)
    A = [np.zeros((N, N)) for _ in range(D + 1)]
    for e in elems:
        for f in elems:
            k = lee_weight(tuple((a - b) % q for a, b in zip(e, f)), q)
            A[k][idx[e], idx[f]] = 1.0
    return A, D


def is_association_scheme(A, D, tol=1e-9):
    """Intersection numbers p_ij^k must be constant on each relation R_k."""
    for i in range(D + 1):
        for j in range(D + 1):
            P = A[i] @ A[j]
            for k in range(D + 1):
                mask = A[k] > 0
                if mask.any():
                    v = P[mask]
                    if v.max() - v.min() > tol:
                        return False, (i, j, k, float(v.min()), float(v.max()))
    return True, None


def distinct_eigs_of_A1(A):
    return len(np.unique(np.round(np.linalg.eigvalsh(A[1]), 6)))


def base_eigenvalues(q):
    """Single-coordinate cycle eigenvalues 2cos(2 pi t / q), distinct."""
    return sorted({round(2 * np.cos(2 * np.pi * t / q), 6) for t in range(q)})


if __name__ == "__main__":
    print("Lee scheme on Z_q^n — P-polynomial test\n")
    print(f"{'q':>3} {'n':>3} {'scheme?':>8} {'#eig(A1)':>9} {'D+1':>5} "
          f"{'P-poly?':>8}")
    for q, n in [(3, 2), (3, 3), (4, 2), (4, 3), (5, 2), (5, 3),
                 (6, 2), (7, 2)]:
        A, D = distance_matrices(q, n)
        sched, _ = is_association_scheme(A, D)
        d = distinct_eigs_of_A1(A)
        ppoly = (d == D + 1) and sched
        print(f"{q:>3} {n:>3} {str(sched):>8} {d:>9} {D + 1:>5} "
              f"{str(ppoly):>8}")

    print("\nWhy: single-coordinate eigenvalues 2cos(2 pi t/q). P-polynomial")
    print("needs their n-fold sums to hit exactly n*floor(q/2)+1 values,")
    print("i.e. the base values must be an arithmetic progression:")
    for q in (3, 4, 5, 6, 7):
        b = base_eigenvalues(q)
        diffs = [round(b[i + 1] - b[i], 4) for i in range(len(b) - 1)]
        ap = len(set(diffs)) <= 1
        print(f"  q={q}: {b}  gaps={diffs}  AP={ap}")
