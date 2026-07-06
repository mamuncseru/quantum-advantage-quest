"""Glued trees (Childs et al. 2003) — the exponential separation that does
NOT come from the Fourier transform.

Graph: two full binary trees of depth d, leaves joined by a random cycle.
Entrance = left root, exit = right root. By symmetry both walks live in the
(2d+2)-dimensional "column" space, which lets us simulate a graph with
2^(d+2) vertices exactly.

Reduced quantum Hamiltonian: path with hopping sqrt(2), except weight 2 on
the middle (glue) edge. The wave packet crosses ballistically in time O(d).

Reduced classical chain: inside either tree a walker has 2 edges pointing
toward the middle and 1 pointing out, so the drift traps it in the
exponentially big middle; P(reach exit in poly(d) steps) = 2^-Omega(d).
"""

import numpy as np


def reduced_adjacency(d):
    """Column-space adjacency of the glued-trees graph: (2d+2) x (2d+2)."""
    L = 2 * d + 2
    A = np.zeros((L, L))
    for j in range(L - 1):
        w = 2.0 if j == d else np.sqrt(2.0)
        A[j, j + 1] = A[j + 1, j] = w
    return A


def quantum_exit_prob(d, times=None):
    """max_t |<exit| e^{-iAt} |entrance>|^2 over a time grid."""
    A = reduced_adjacency(d)
    lam, V = np.linalg.eigh(A)
    if times is None:
        times = np.linspace(0, 4 * d, 400)
    entrance = V.T[:, 0]                      # V^T e_0 : entrance in eigenbasis
    exit_row = V[-1, :]                       # <exit| V
    probs = [abs(exit_row @ (np.exp(-1j * lam * t) * entrance)) ** 2
             for t in times]
    i = int(np.argmax(probs))
    return probs[i], times[i]


def classical_column_chain(d):
    """Transition matrix of the classical random walk, collapsed to columns,
    with the exit made absorbing. Column j holds P(j -> .) in row j."""
    L = 2 * d + 2
    P = np.zeros((L, L))
    P[0, 1] = 1.0                                     # entrance root: degree 2, both forward
    for j in range(1, d + 1):                         # left side incl. leaves: 2 of 3 edges forward
        P[j, j + 1] = 2 / 3
        P[j, j - 1] = 1 / 3
    for j in range(d + 1, L - 1):                     # right side: only 1 of 3 edges forward
        P[j, j + 1] = 1 / 3
        P[j, j - 1] = 2 / 3
    P[L - 1, L - 1] = 1.0                             # exit absorbs
    return P


def classical_exit_prob(d, steps):
    """P(classical walk from entrance hits exit within `steps` steps)."""
    P = classical_column_chain(d)
    dist = np.zeros(P.shape[0])
    dist[0] = 1.0
    for _ in range(steps):
        dist = dist @ P
    return dist[-1]


if __name__ == "__main__":
    print(f"{'d':>3} {'quantum p_exit':>15} {'t*':>6} {'classical p (d^3 steps)':>24} {'ratio':>12}")
    for d in (4, 8, 12, 16, 20):
        pq, tstar = quantum_exit_prob(d)
        pc = classical_exit_prob(d, steps=d ** 3)
        print(f"{d:>3} {pq:>15.4f} {tstar:>6.1f} {pc:>24.3e} {pq/pc:>12.1f}")
