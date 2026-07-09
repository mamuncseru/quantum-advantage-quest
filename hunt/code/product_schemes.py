"""A3: which Cartesian products of graphs are distance-regular?

A coordinate-decomposable DQI metric (weight = sum of per-block weights)
has a P-polynomial scheme iff the Cartesian product of the per-block
unit-shell graphs is DISTANCE-REGULAR. This module computes DR directly,
extracts witnesses when it fails, and compares intersection arrays.

Claim under test (proof: hunt/notes/A3-product-theorem.md): a Cartesian
product of >= 2 connected graphs is distance-regular iff every factor has
the intersection array of a Hamming graph H(d_i, q) with one COMMON q —
by Egawa's characterization, iff the product is Hamming H(n,q) or Doob
D(m,n). The Lee kill (cycles have c_2 = 1 for q >= 5) is a special case;
the Clebsch graph is the instructive near-miss: AP eigenvalues with the
right common difference, yet its square fails the intersection axiom.

Run: .venv/bin/python hunt/code/product_schemes.py
"""

from itertools import product

import numpy as np


# ---------------------------------------------------------------- blocks

def complete_graph(q):
    return np.ones((q, q)) - np.eye(q)


def cycle(q):
    A = np.zeros((q, q))
    for i in range(q):
        A[i, (i + 1) % q] = A[(i + 1) % q, i] = 1.0
    return A


def cayley_graph(gens, conn):
    """Cayley graph on Z_{g_1} x ... x Z_{g_r} with connection set conn
    (closed under negation)."""
    elems = list(product(*[range(g) for g in gens]))
    idx = {e: i for i, e in enumerate(elems)}
    A = np.zeros((len(elems), len(elems)))
    for e in elems:
        for s in conn:
            f = tuple((a + b) % g for a, b, g in zip(e, s, gens))
            A[idx[e], idx[f]] = 1.0
    return A


def shrikhande():
    """SRG(16,6,2,2) on Z_4^2 — same parameters as the 4x4 rook graph
    H(2,4), not isomorphic to it. The q=4 exception."""
    conn = [(1, 0), (3, 0), (0, 1), (0, 3), (1, 1), (3, 3)]
    return cayley_graph((4, 4), conn)


def clebsch():
    """SRG(16,5,0,2) on Z_2^4 (folded 5-cube). Eigenvalues 5,1,-3 — an AP
    with common difference 4, like Shrikhande's 6,2,-2."""
    conn = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1),
            (1, 1, 1, 1)]
    return cayley_graph((2, 2, 2, 2), conn)


def cartesian(A, B):
    return np.kron(A, np.eye(B.shape[0])) + np.kron(np.eye(A.shape[0]), B)


def doob(m, n):
    """Doob graph D(m,n): m Shrikhande factors x n K_4 factors."""
    A = None
    for blk in [shrikhande()] * m + [complete_graph(4)] * n:
        A = blk if A is None else cartesian(A, blk)
    return A


# ------------------------------------------------------------ machinery

def distances(A):
    N = A.shape[0]
    dist = np.full((N, N), -1, dtype=int)
    frontier = np.eye(N, dtype=bool)
    reached = frontier.copy()
    dist[frontier] = 0
    d = 0
    while frontier.any():
        d += 1
        frontier = ((frontier @ A) > 0) & ~reached
        dist[frontier] = d
        reached |= frontier
    return dist


def is_distance_regular(A, dist=None, tol=1e-9):
    """Check |{z : z~x, d(z,y)=j}| is constant over pairs at distance k,
    for all j,k — the full DR condition. Witness on failure."""
    if dist is None:
        dist = distances(A)
    diam = dist.max()
    for j in range(diam + 1):
        C = A @ (dist == j).astype(float)
        for k in range(diam + 1):
            vals = C[dist == k]
            if vals.size and vals.max() - vals.min() > tol:
                return False, (j, k, float(vals.min()), float(vals.max()))
    return True, None


def intersection_array(A, dist=None):
    """(b_0..b_{d-1}; c_1..c_d) — only valid if DR."""
    if dist is None:
        dist = distances(A)
    diam = dist.max()
    b, c = [], []
    for k in range(diam + 1):
        pairs = np.argwhere(dist == k)
        x, y = pairs[0]
        nz = np.nonzero(A[x])[0]
        if k < diam:
            b.append(int((dist[nz, y] == k + 1).sum()))
        if k > 0:
            c.append(int((dist[nz, y] == k - 1).sum()))
    return b, c


def hamming_array(d, q):
    return ([(d - j) * (q - 1) for j in range(d)], list(range(1, d + 1)))


def distinct_eigs(A):
    return sorted(set(np.round(np.linalg.eigvalsh(A), 6)), reverse=True)


# ----------------------------------------------------------------- main

if __name__ == "__main__":
    print("Cartesian products: distance-regular or not?\n")
    cases = [
        ("K4 [] K4  = H(2,4)", cartesian(complete_graph(4),
                                         complete_graph(4))),
        ("Shrikhande = D(1,0)", shrikhande()),
        ("Sh [] K4  = D(1,1)", doob(1, 1)),
        ("Sh [] Sh  = D(2,0)", doob(2, 0)),
        ("Sh[]Sh[]K4 = D(2,1)", doob(2, 1)),
        ("Clebsch (alone)", clebsch()),
        ("Clebsch [] Clebsch", cartesian(clebsch(), clebsch())),
        ("Clebsch [] K4", cartesian(clebsch(), complete_graph(4))),
        ("C5 [] C5 (Lee q=5)", cartesian(cycle(5), cycle(5))),
    ]
    print(f"{'graph':>20} {'N':>5} {'DR?':>5} {'diam':>5} "
          f"{'array = H(d,q)?':>16}  witness (j,k,min,max)")
    for name, A in cases:
        dist = distances(A)
        dr, wit = is_distance_regular(A, dist)
        diam = int(dist.max())
        match = ""
        if dr:
            b, c = intersection_array(A, dist)
            for q in (2, 3, 4, 5):
                if (b, c) == hamming_array(diam, q):
                    match = f"H({diam},{q})"
        print(f"{name:>20} {A.shape[0]:>5} {str(dr):>5} {diam:>5} "
              f"{match:>16}  {wit if wit else ''}")

    print("\nBlock eigenvalues (all APs with common difference 4):")
    for name, A in [("Shrikhande", shrikhande()), ("K4", complete_graph(4)),
                    ("Clebsch", clebsch())]:
        print(f"  {name:>10}: {distinct_eigs(A)}")
    print("\nClebsch has the AP property yet Clebsch[]Clebsch is not DR:")
    print("the eigenvalue-count condition is necessary, NOT sufficient.")
    print("The binding constraint is intersection-number homogeneity, and")
    print("it forces every factor to carry a Hamming intersection array")
    print("(proof in notes/A3-product-theorem.md) => Hamming or Doob only.")
