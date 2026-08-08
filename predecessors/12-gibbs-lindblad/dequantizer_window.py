"""“Break the dequantizer, keep the mixer” — the recipe, executed.

The autopsy calls Bakshi-Tan "the template result ... executed exactly once
in the literature. Repeatable by construction." A template nobody has run is
a claim, so this file runs one.

The recipe, stated as a procedure:

  1. take a family H(lambda) with a knob,
  2. measure what the CLASSICAL methods pay as lambda turns,
  3. measure whether the QUANTUM Lindbladian still mixes,
  4. look for a window where (2) blows up and (3) does not.

The knob used here is **frustration**: start from a Heisenberg chain, which
is bipartite and therefore sign-problem-free (see `gibbs_gap.py`), and close
the loop. Frustration is what a sign problem is made of, so this is the
smallest honest knob that moves the classical cost without touching the
locality or the norm of the Hamiltonian.

WHAT THIS IS NOT: a reproduction of Bakshi-Tan's theorem, whose knob is
strong on-site fields and whose classical target is the specific
counting-to-sampling reduction. This is the *shape* of their argument run on
a family small enough to compute exactly — which is what makes the shape
checkable, and what a hunt-phase candidate would have to clear before anyone
writes a proof.

Run:  .venv/bin/python predecessors/12-gibbs-lindblad/dequantizer_window.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from qsim import X, Y, Z  # noqa: E402

from davies import site_op  # noqa: E402
from gibbs_gap import (average_sign, davies_gap, mixing_time,  # noqa: E402
                       qmc_overhead, thermal_mutual_information)


# ------------------------------------------------------------- the knob ---

def frustration_family(n, lam, seed=1):
    """Heisenberg chain, plus `lam` times the bond that closes the loop.

    lam = 0 is an open chain: bipartite, sign-free, classically comfortable.
    lam = 1 closes an odd cycle when n is odd, which is frustration in its
    smallest form. The locality and the operator norm barely move; only the
    *sign structure* does, which is what makes it a clean knob.
    """
    rng = np.random.default_rng(seed)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            H += site_op(P, i, n) @ site_op(P, i + 1, n)
    if lam:
        for P in (X, Y, Z):
            H += lam * site_op(P, 0, n) @ site_op(P, n - 1, n)
    for i in range(n):
        H += 0.15 * rng.normal() * site_op(Z, i, n)
    return H


def profile(n, lam, beta):
    """Both sides of the ledger for one (lambda, beta)."""
    H = frustration_family(n, lam)
    return dict(
        lam=float(lam), beta=float(beta),
        gap=davies_gap(H, beta),
        mixing=mixing_time(H, beta),
        sign=average_sign(H, beta),
        qmc=qmc_overhead(H, beta),
        mutual=thermal_mutual_information(H, beta),
        norm=float(np.linalg.norm(H, 2)),
    )


def knob_sweep(n=3, beta=3.0, lams=(0.0, 0.25, 0.5, 0.75, 1.0)):
    return [profile(n, lam, beta) for lam in lams]


def window_scan(n=3, lams=(0.0, 0.5, 1.0), betas=(0.5, 1.0, 2.0, 4.0)):
    """The (lambda, beta) map: where is the conjunction satisfied?"""
    return [[profile(n, lam, b) for b in betas] for lam in lams]


# ------------------------------------------------- the recipe's verdict ---

def is_window(row, qmc_threshold=100.0, gap_floor=0.25):
    """Both conditions at once: classical cost up, quantum cost still low.

    Neither condition alone is interesting — a hard classical problem where
    the Lindbladian also stalls is just a hard problem, and a fast mixer on
    an easy instance is a demonstration, not an advantage.
    """
    return bool(row["qmc"] >= qmc_threshold and row["gap"] >= gap_floor)


def find_window(n=3, lams=(0.0, 0.25, 0.5, 0.75, 1.0),
                betas=(0.5, 1.0, 2.0, 3.0, 4.0), **kw):
    """Every (lambda, beta) cell where the recipe's conjunction holds."""
    hits = []
    for lam in lams:
        for b in betas:
            row = profile(n, lam, b)
            if is_window(row, **kw):
                hits.append(row)
    return hits


def gap_cost_ratio(row):
    """How much cheaper the quantum route is, on these two proxies alone.

    Deliberately crude: the quantum side's cost is the mixing time and the
    classical side's is the sign overhead. It is a ratio of two different
    kinds of thing, and it is quoted only to show which direction the knob
    moves them.
    """
    return row["qmc"] / max(row["mixing"], 1e-12)


# ----------------------------------------------------------------- demo ----

def _demo():
    n, beta = 3, 3.0
    print("1 · TURNING THE KNOB: WHAT EACH SIDE PAYS\n")
    print(f"   Heisenberg chain on {n} sites, closing bond weight λ, β = {beta}\n")
    print(f"   {'λ':>6} {'‖H‖':>7} {'<sign>':>10} {'QMC overhead':>14} "
          f"{'Davies gap':>12} {'mixing time':>13}")
    for row in knob_sweep(n=n, beta=beta):
        print(f"   {row['lam']:>6.2f} {row['norm']:>7.2f} {row['sign']:>10.5f} "
              f"{row['qmc']:>14,.0f} {row['gap']:>12.4f} "
              f"{row['mixing']:>13.2f}")
    print("\n   The operator norm barely moves; the sign collapses; the gap")
    print("   stays open. That is the recipe's conjunction, and it is the")
    print("   whole content of 'break the dequantizer, keep the mixer'.\n")

    print("2 · THE WINDOW IN (λ, β)\n")
    lams = (0.0, 0.5, 1.0)
    betas = (0.5, 1.0, 2.0, 4.0)
    print("   QMC overhead (classical cost):\n")
    print("   " + "λ / β".rjust(8) + "".join(f"{b:>12.1f}" for b in betas))
    scan = window_scan(n=n, lams=lams, betas=betas)
    for lam, rows in zip(lams, scan):
        print(f"   {lam:>8.2f}" + "".join(f"{r['qmc']:>12,.0f}" for r in rows))
    print("\n   Davies gap (quantum cost is 1/this):\n")
    print("   " + "λ / β".rjust(8) + "".join(f"{b:>12.1f}" for b in betas))
    for lam, rows in zip(lams, scan):
        print(f"   {lam:>8.2f}" + "".join(f"{r['gap']:>12.4f}" for r in rows))

    hits = find_window(n=n)
    print(f"\n   cells satisfying BOTH conditions "
          f"(QMC overhead ≥ 100 and gap ≥ 0.25): {len(hits)}")
    for row in hits[:6]:
        print(f"     λ = {row['lam']:.2f}, β = {row['beta']:.1f}:  "
              f"classical ×{row['qmc']:,.0f},  mixing time "
              f"{row['mixing']:.1f}")

    print("\n3 · WHAT THIS DOES AND DOES NOT ESTABLISH\n")
    print("   DOES: the conjunction is achievable, on a family small enough")
    print("   to compute exactly, with a knob that moves the sign structure")
    print("   and leaves the locality and norm alone. That is the template,")
    print("   and it is repeatable — which is what the autopsy claims.")
    print()
    print("   DOES NOT: three sites is not an asymptotic statement, the QMC")
    print("   overhead is a proxy for one classical method rather than for")
    print("   all of them, and a gap measured at n = 3 says nothing about")
    print("   n = 300. **Proving the gap stays open is still the frontier**,")
    print("   and no amount of exact diagonalisation substitutes for it.")
    print()
    print("   The useful output is the SHAPE: a candidate for this ground")
    print("   has to move a classical cost by orders of magnitude while")
    print("   leaving the mixing time flat, and both halves must be measured")
    print("   before either is claimed.")


if __name__ == "__main__":
    _demo()
