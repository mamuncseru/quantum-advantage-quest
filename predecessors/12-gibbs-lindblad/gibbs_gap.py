"""The gap, and the two classical walls — measured on small systems.

The autopsy says "prove the gap is the entire remaining frontier" and lists
two mechanisms of classical failure (sign problem for Monte Carlo,
entanglement for tensor networks). None of the three is a number anywhere on
the page. This file makes all three numbers.

  1. **The Davies gap**, as a function of inverse temperature and system
     size. This is the mixing time, and therefore the algorithm's cost. The
     measurement that matters is not "there is a gap" — `davies.py` already
     shows that — it is **how the gap behaves as beta grows**, because that
     is where the frontier is.

  2. **The sign problem**, quantified. The average sign of a quantum Monte
     Carlo simulation is Z / Z_abs, where Z_abs is the partition function of
     the stoquastic-ised Hamiltonian (off-diagonals replaced by minus their
     magnitudes). Its decay is exactly the exponential cost QMC pays, and it
     is computable exactly at these sizes.

  3. **The entanglement of the Gibbs state**, which is what a tensor network
     has to store — the same diagnostic autopsy 09 used for dynamics, asked
     here of a thermal state.

The point of putting all three in one file: an advantage on this ground
needs the gap to stay open while BOTH classical mechanisms degrade, and
that conjunction is checkable.

Run:  .venv/bin/python predecessors/12-gibbs-lindblad/gibbs_gap.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from qsim import I2, X, Y, Z  # noqa: E402

from davies import (davies_superoperator, gibbs_state,  # noqa: E402
                    heisenberg_with_fields, site_op, spectral_gap)


# ------------------------------------------------------------ models ------

def transverse_ising(n, g=1.0, J=1.0, field=0.0, seed=0):
    """H = -J sum Z Z - g sum X - field sum (random) Z.

    `field` is the knob Bakshi-Tan turn: strong on-site fields are what
    break the classical counting-to-sampling reduction while leaving the
    quantum Lindbladian mixing.
    """
    rng = np.random.default_rng(seed)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        H -= J * site_op(Z, i, n) @ site_op(Z, i + 1, n)
    for i in range(n):
        H -= g * site_op(X, i, n)
    if field:
        for i in range(n):
            H += field * rng.normal(0, 1.0) * site_op(Z, i, n)
    return H


def frustrated_afm(n=3):
    """All-pairs antiferromagnetic Heisenberg — frustrated, hence signful.

    Frustration is the point. A Heisenberg chain is *bipartite*, and the
    Marshall sign rule gauges its sign problem away entirely — so the chain
    `davies.py` demonstrates on is not a hard instance for Monte Carlo, a
    fact measured in the demo below. Close the loop into an odd cycle and
    the sign problem appears at once.
    """
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        for j in range(i + 1, n):
            for P in (X, Y, Z):
                H += site_op(P, i, n) @ site_op(P, j, n)
    return H


def default_couplings(n):
    """One X and one Y jump per site: ergodic, and the standard choice."""
    return [site_op(X, i, n) for i in range(n)] + \
           [site_op(Y, i, n) for i in range(n)]


# ------------------------------------------------------------- the gap ----

def davies_gap(H, beta, couplings=None):
    """Spectral gap of the Davies generator — the inverse mixing time."""
    n = int(np.log2(H.shape[0]))
    couplings = default_couplings(n) if couplings is None else couplings
    return float(spectral_gap(davies_superoperator(H, couplings, beta)))


def mixing_time(H, beta, couplings=None, eps=1e-3):
    """~log(1/eps)/gap: the time the Lindbladian needs to get within eps."""
    g = davies_gap(H, beta, couplings)
    return float("inf") if g <= 0 else float(np.log(1 / eps) / g)


def gap_vs_beta(H, betas):
    return [(float(b), davies_gap(H, float(b))) for b in betas]


def gap_scaling_in_beta(H, betas=(0.5, 1.0, 2.0, 4.0)):
    """Fitted exponent of gap ~ beta^(-a). Cooling costs mixing time, and
    how much is the whole question."""
    bs = np.array(betas, dtype=float)
    gs = np.array([davies_gap(H, float(b)) for b in bs])
    m = gs > 0
    return float(-np.polyfit(np.log(bs[m]), np.log(gs[m]), 1)[0])


# -------------------------------------------------- wall 1: the sign ------

def stoquasticised(H):
    """Off-diagonal entries replaced by minus their magnitudes.

    The resulting Hamiltonian has no sign problem by construction, and its
    partition function is the denominator Monte Carlo actually samples.
    """
    D = np.diag(np.diag(H))
    off = H - D
    return D - np.abs(off)


def average_sign(H, beta):
    """<sign> = Z / Z_abs — the exponential price QMC pays.

    Equals 1 exactly when the model is sign-problem-free, and decays
    exponentially in beta and in system size when it is not.

    Worth stating precisely, because the obvious reading is wrong:
    **non-commuting does not mean signful**. A bipartite Heisenberg chain is
    thoroughly non-commuting and yet has <sign> = 1 to machine precision,
    because the Marshall sign rule is a basis change that removes the
    problem. What creates a sign problem is *frustration* (odd cycles) or
    fermionic exchange — see `frustrated_afm`.
    """
    lam = np.linalg.eigvalsh(H)
    lam_abs = np.linalg.eigvalsh(stoquasticised(H))
    shift = min(lam.min(), lam_abs.min())
    Z = np.exp(-beta * (lam - shift)).sum()
    Z_abs = np.exp(-beta * (lam_abs - shift)).sum()
    return float(Z / Z_abs)


def qmc_overhead(H, beta):
    """1/<sign>^2 — the number of samples the sign problem multiplies by."""
    s = average_sign(H, beta)
    return float("inf") if s <= 0 else 1.0 / s ** 2


def is_stoquastic(H, tol=1e-12):
    off = H - np.diag(np.diag(H))
    return bool(np.all(np.real(off) <= tol) and
                np.abs(np.imag(off)).max() < tol)


# ------------------------------------------ wall 2: the entanglement ------

def thermal_mutual_information(H, beta, cut=None):
    """I(A:B) of the Gibbs state across a cut, in bits.

    The thermal analogue of autopsy 09's diagnostic: how much correlation a
    classical description has to carry. It falls as the temperature rises —
    which is exactly why high-temperature Gibbs states are classically easy
    and the advantage has to live at intermediate beta.
    """
    n = int(np.log2(H.shape[0]))
    cut = n // 2 if cut is None else cut
    rho = gibbs_state(H, beta)
    dA, dB = 2 ** cut, 2 ** (n - cut)
    t = rho.reshape(dA, dB, dA, dB)
    rhoA = np.einsum("ijkj->ik", t)
    rhoB = np.einsum("ijil->jl", t)

    def ent(r):
        ev = np.linalg.eigvalsh(r)
        ev = ev[ev > 1e-14]
        return float(-(ev * np.log2(ev)).sum())

    return ent(rhoA) + ent(rhoB) - ent(rho)


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · THE GAP IS THE COST, AND COOLING IS WHAT COSTS\n")
    n = 3
    H = heisenberg_with_fields(n)
    print(f"   Heisenberg chain with random fields, n = {n}\n")
    print(f"   {'β':>7} {'Davies gap':>13} {'mixing time':>14}")
    for b in (0.25, 0.5, 1.0, 2.0, 4.0):
        print(f"   {b:>7.2f} {davies_gap(H, b):>13.5f} "
              f"{mixing_time(H, b):>14.2f}")
    print(f"\n   fitted gap ~ β^-{gap_scaling_in_beta(H):.2f}: the sampler")
    print("   slows down as it cools, which is the same story classical")
    print("   MCMC tells. **Proving this gap stays open for large n is the")
    print("   entire remaining frontier of this ground** — nothing on this")
    print("   page substitutes for that theorem.\n")

    print("2 · WALL ONE: THE SIGN PROBLEM, PRICED — AND A CORRECTION\n")
    print(f"   {'model':>36} {'β = 1':>10} {'β = 2':>10} {'β = 4':>10}")
    for label, Hx in (
            ("transverse Ising (stoquastic)", transverse_ising(3)),
            ("Heisenberg CHAIN + fields (bipartite)",
             heisenberg_with_fields(3)),
            ("triangle AFM (frustrated)", frustrated_afm(3)),
            ("all-pairs AFM, n = 4", frustrated_afm(4))):
        row = "".join(f"{average_sign(Hx, b):>10.5f}" for b in (1.0, 2.0, 4.0))
        print(f"   {label:>36}{row}")
    print("\n   Read the second row carefully. The Heisenberg chain is")
    print("   thoroughly non-commuting and its average sign is 1.00000 to")
    print("   machine precision: it is BIPARTITE, so the Marshall sign rule")
    print("   gauges the sign problem away. **Non-commuting does not mean")
    print("   signful** — and the chain `davies.py` demonstrates on is")
    print("   therefore a witness for the mechanism, not for the hardness.")
    print("   Monte Carlo handles it comfortably.")
    print("\n   Frustration is what costs. Close the chain into a triangle")
    print("   and the sign decays exponentially:")
    Hf = frustrated_afm(3)
    for b in (1.0, 2.0, 4.0):
        print(f"     β = {b:>4.1f}:  <sign> = {average_sign(Hf, b):.5f}, "
              f"QMC overhead = {qmc_overhead(Hf, b):,.0f}x")
    print()

    print("3 · WALL TWO: THE ENTANGLEMENT OF THE THERMAL STATE\n")
    print(f"   {'β':>7} {'mutual information (bits)':>28}")
    for b in (0.1, 0.5, 1.0, 2.0, 4.0, 8.0):
        print(f"   {b:>7.2f} "
              f"{thermal_mutual_information(heisenberg_with_fields(4), b):>28.4f}")
    print("\n   Near-zero at high temperature — which is why the")
    print("   provably-easy atlas covers that regime — and growing as the")
    print("   state cools toward the ground state. The advantage has to live")
    print("   in between: cold enough that correlations are real, warm")
    print("   enough that the Lindbladian still mixes.\n")

    print("4 · THE CONJUNCTION AN ADVANTAGE NEEDS\n")
    Hh = heisenberg_with_fields(3)
    print(f"   {'β':>7} {'Davies gap':>12} {'QMC overhead':>14} "
          f"{'mutual info':>13}")
    for b in (0.25, 1.0, 4.0):
        print(f"   {b:>7.2f} {davies_gap(Hh, b):>12.5f} "
              f"{qmc_overhead(Hh, b):>14.1f} "
              f"{thermal_mutual_information(Hh, b):>13.4f}")
    print("\n   Read the rows together. The quantum cost is 1/gap and the")
    print("   classical costs are the other two columns. An advantage needs")
    print("   the first to stay small while the others blow up — and both")
    print("   move in the same direction as β. That tension is this ground's")
    print("   whole research programme, and `dequantizer_window.py` turns a")
    print("   knob that separates them.")


if __name__ == "__main__":
    _demo()
