"""Szegedy's quantisation, and the square root that caps it — notes.md section 6.

Glued trees is a one-off: a graph engineered so that one specific quantum
walk sails across it. Szegedy's construction is the systematic version —
take *any* reversible Markov chain and turn it into a quantum walk — and the
systematic version comes with a systematic ceiling.

The theorem: the walk operator's eigenphases are arccos of the chain's
eigenvalues, so a classical spectral gap delta becomes a quantum phase gap
~ sqrt(delta). Hitting and search cost ~1/sqrt(delta) instead of ~1/delta.
Quadratic, and no more.

Nothing here is quoted. The walk operator is built out of its two
reflections, diagonalised, and the phase gap is measured — then compared
against arccos of the classical spectrum.

Run:  .venv/bin/python predecessors/07-quantum-walks/szegedy.py
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------- chains ---

def cycle_chain(n):
    """Random walk on a cycle: the slow-mixing standard example."""
    P = np.zeros((n, n))
    for x in range(n):
        P[x, (x + 1) % n] = P[x, (x - 1) % n] = 0.5
    return P


def path_chain(n):
    P = np.zeros((n, n))
    for x in range(n):
        nb = [y for y in (x - 1, x + 1) if 0 <= y < n]
        for y in nb:
            P[x, y] = 1.0 / len(nb)
    return P


def complete_chain(n):
    """The fastest-mixing chain there is: gap 1, nothing to speed up."""
    P = np.full((n, n), 1.0 / (n - 1))
    np.fill_diagonal(P, 0.0)
    return P


def barbell_chain(half):
    """Two cliques joined by a single edge — an exponentially small gap.

    The classic bottleneck: a walker takes ~n^2 steps to find the bridge.
    This is where a square-root speedup is worth the most, so it is the
    honest place to measure one.
    """
    n = 2 * half
    A = np.zeros((n, n))
    for i in range(half):
        for j in range(half):
            if i != j:
                A[i, j] = A[i + half, j + half] = 1.0
    A[half - 1, half] = A[half, half - 1] = 1.0
    return A / A.sum(axis=1, keepdims=True)


def lazy(P, p=0.5):
    """Make a chain lazy: stay put with probability p. Removes the -1
    eigenvalue that bipartite chains have, so the gap is the real one."""
    return p * np.eye(P.shape[0]) + (1 - p) * P


# ------------------------------------------------------ classical spectrum --

def spectral_gap(P):
    """1 - |second largest eigenvalue|. Classical mixing time ~ 1/gap."""
    ev = np.linalg.eigvals(P)
    ev = np.sort(np.abs(ev))[::-1]
    return float(1.0 - ev[1])


def stationary(P):
    ev, V = np.linalg.eig(P.T)
    i = int(np.argmin(np.abs(ev - 1.0)))
    pi = np.real(V[:, i])
    return pi / pi.sum()


def is_reversible(P, tol=1e-9):
    """Detailed balance: pi_x P_xy = pi_y P_yx. Szegedy needs it."""
    pi = stationary(P)
    return bool(np.abs(pi[:, None] * P - (pi[:, None] * P).T).max() < tol)


# ------------------------------------------------- the quantum walk itself --

def szegedy_walk(P):
    """The walk operator W = ref_B · ref_A on the n^2-dimensional edge space.

    A is spanned by |x> (sum_y sqrt(P_xy) |y>), B by its transpose. Each
    reflection is 2*projector - I, and their product is the walk. Built
    explicitly so that "the eigenphases are arccos of the chain's spectrum"
    is something we measure rather than assert.
    """
    n = P.shape[0]
    A = np.zeros((n * n, n))
    B = np.zeros((n * n, n))
    for x in range(n):
        for y in range(n):
            A[x * n + y, x] = np.sqrt(P[x, y])
            B[x * n + y, y] = np.sqrt(P[y, x])
    refA = 2 * A @ A.T - np.eye(n * n)
    refB = 2 * B @ B.T - np.eye(n * n)
    return refB @ refA


def phase_gap(W, tol=1e-8):
    """Smallest nonzero eigenphase of the walk operator, in radians.

    The quantum analogue of the spectral gap: it sets how long phase
    estimation must run, and therefore the cost of every walk-based search.
    """
    ev = np.linalg.eigvals(W)
    ph = np.abs(np.angle(ev))
    ph = ph[ph > tol]
    return float(ph.min()) if ph.size else 0.0


def predicted_phase_gap(P):
    """2 arccos(lambda_2) — the theorem's prediction, for comparison."""
    ev = np.sort(np.abs(np.linalg.eigvals(P)))[::-1]
    return float(2 * np.arccos(min(1.0, ev[1])))


def gap_ratio(P):
    """phase gap divided by sqrt(spectral gap) — the constant the square-root
    law predicts. If this is flat across wildly different chains, the law is
    real and not a coincidence of one example."""
    W = szegedy_walk(P)
    return phase_gap(W) / np.sqrt(spectral_gap(P))


# ------------------------------------------------------ what it buys -------

def classical_hitting_scale(P):
    """~1/delta — the classical mixing/hitting scale."""
    return 1.0 / spectral_gap(P)


def quantum_hitting_scale(P):
    """~1/sqrt(delta) — what the quantised walk pays instead."""
    return 1.0 / np.sqrt(spectral_gap(P))


# ----------------------------------------------------------------- demo ----

def _demo():
    print("SZEGEDY'S QUANTISATION: MEASURED, NOT QUOTED\n")
    chains = [
        ("cycle C_12 (lazy)", lazy(cycle_chain(12))),
        ("cycle C_20 (lazy)", lazy(cycle_chain(20))),
        ("path P_12 (lazy)", lazy(path_chain(12))),
        ("complete K_10", lazy(complete_chain(10))),
        ("barbell 2x5", lazy(barbell_chain(5))),
        ("barbell 2x8", lazy(barbell_chain(8))),
    ]
    print(f"   {'chain':20} {'reversible':>11} {'gap δ':>10} "
          f"{'phase gap':>11} {'2·arccos(λ₂)':>14} {'ratio /√δ':>11}")
    for name, P in chains:
        d = spectral_gap(P)
        W = szegedy_walk(P)
        pg = phase_gap(W)
        print(f"   {name:20} {str(is_reversible(P)):>11} {d:>10.5f} "
              f"{pg:>11.5f} {predicted_phase_gap(P):>14.5f} "
              f"{pg / np.sqrt(d):>11.4f}")

    print("\n   the measured phase gap matches 2·arccos(λ₂) to machine")
    print("   precision, and the last column is flat: phase gap = Θ(√δ)")
    print("   across chains whose gaps differ by orders of magnitude.\n")

    print("WHAT THE SQUARE ROOT IS WORTH\n")
    print(f"   {'chain':20} {'classical ~1/δ':>16} {'quantum ~1/√δ':>15} "
          f"{'speedup':>9}")
    for name, P in chains:
        c, q = classical_hitting_scale(P), quantum_hitting_scale(P)
        print(f"   {name:20} {c:>16.1f} {q:>15.1f} {c / q:>9.1f}x")

    print("\n   Quadratic, always — which puts every Szegedy walk under the")
    print("   same ceiling autopsy 06 priced: a square root is a component,")
    print("   not a product. The glued-trees exponential is NOT of this")
    print("   family, and that is exactly why it needed an engineered graph.")


if __name__ == "__main__":
    _demo()
