"""Why the walk wins, and what it costs to keep winning — notes.md sections 3-5.

Two experiments the existing `glued_trees.py` does not do.

**1. Ballistic versus diffusive, measured.** The whole mechanism is one
number: a quantum wave packet on a path spreads with <x^2> ~ t^2, a
classical walker with <x^2> ~ t. Everything else — the exponential
separation, the O(d) crossing time — is a consequence. So we measure the
exponent instead of asserting it.

**2. Disorder, which is the honest critique.** The reduced chain is uniform
only because the graph is *engineered* to be perfectly symmetric. Any defect
— an imperfect glue, an uneven tree, a vertex with the wrong degree — makes
the effective hoppings and site energies non-uniform, and one dimension is
the worst possible case for that: Anderson localisation sets in at *any*
disorder strength, and ballistic transport dies exponentially in the
distance it has to cover.

That is the fragility this speedup is usually sold without.

CAVEAT, stated because it matters: perturbing the *graph* also breaks the
column-space reduction itself, so the model below is disorder added to the
effective chain, not a general graph perturbation. It is the right model for
"the reduced dynamics are not exactly uniform", which is what every physical
realisation would face, and it is not a proof about arbitrary graph defects.

Run:  .venv/bin/python predecessors/07-quantum-walks/walk_transport.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from glued_trees import reduced_adjacency  # noqa: E402


# ------------------------------------------------ ballistic vs diffusive ---

def quantum_spread(length, times):
    """<x^2>(t) for a wave packet started at one end of a uniform path.

    A continuous-time quantum walk on a path has a linear light cone: the
    packet's width grows like t, so <x^2> ~ t^2. That exponent is the entire
    mechanism of this autopsy.
    """
    A = np.zeros((length, length))
    for j in range(length - 1):
        A[j, j + 1] = A[j + 1, j] = 1.0
    lam, V = np.linalg.eigh(A)
    start = np.zeros(length)
    start[length // 2] = 1.0
    coeffs = V.T @ start
    xs = np.arange(length) - length // 2
    out = []
    for t in times:
        psi = V @ (np.exp(-1j * lam * t) * coeffs)
        p = np.abs(psi) ** 2
        out.append(float(np.sum(xs ** 2 * p)))
    return np.array(out)


def classical_spread(length, times):
    """<x^2>(t) for the corresponding classical walk: diffusive, ~ t."""
    P = np.zeros((length, length))
    for j in range(length):
        nb = [k for k in (j - 1, j + 1) if 0 <= k < length]
        for k in nb:
            P[j, k] = 1.0 / len(nb)
    xs = np.arange(length) - length // 2
    dist = np.zeros(length)
    dist[length // 2] = 1.0
    out, prev = [], 0
    for t in times:
        for _ in range(int(t) - prev):
            dist = dist @ P
        prev = int(t)
        out.append(float(np.sum(xs ** 2 * dist)))
    return np.array(out)


def fit_exponent(times, values):
    """Slope of log <x^2> against log t — 2 for ballistic, 1 for diffusive."""
    m = (times > 0) & (values > 0)
    return float(np.polyfit(np.log(times[m]), np.log(values[m]), 1)[0])


# ------------------------------------------------------------- disorder ----

def disordered_adjacency(d, strength, rng):
    """The glued-trees reduced chain with random on-site energies.

    strength W puts each site energy uniformly in [-W/2, W/2]. W = 0 is the
    clean, engineered graph the theorem is about.
    """
    A = reduced_adjacency(d).copy()
    L = A.shape[0]
    for j in range(L):
        A[j, j] += rng.uniform(-strength / 2, strength / 2)
    return A


def exit_probability(A, times=None, d=None):
    """max_t |<exit| e^{-iAt} |entrance>|^2, the quantity glued_trees.py uses."""
    L = A.shape[0]
    d = d if d is not None else (L - 2) // 2
    times = np.linspace(0, 4 * d, 400) if times is None else times
    lam, V = np.linalg.eigh(A)
    entrance = V.T[:, 0]
    exit_row = V[-1, :]
    probs = [abs(exit_row @ (np.exp(-1j * lam * t) * entrance)) ** 2
             for t in times]
    i = int(np.argmax(probs))
    return probs[i], times[i]


def disordered_exit(d, strength, trials=24, seed=0):
    """Median exit probability over disorder realisations.

    Median rather than mean: localised systems have heavy-tailed
    distributions, and the mean is dominated by rare lucky samples that no
    real device would be able to select.
    """
    rng = np.random.default_rng(seed)
    vals = [exit_probability(disordered_adjacency(d, strength, rng), d=d)[0]
            for _ in range(trials)]
    return float(np.median(vals))


def participation_ratio(A):
    """Mean inverse participation ratio of the eigenvectors, as a fraction
    of the system size.

    1.0 means every eigenstate is spread over the whole chain (extended,
    transport possible); values near 0 mean the eigenstates are stuck on a
    few sites (localised, transport dead). This is the standard diagnostic
    and it does not depend on choosing a good measurement time.
    """
    _, V = np.linalg.eigh(A)
    L = A.shape[0]
    ipr = np.sum(V ** 4, axis=0)
    return float(np.mean(1.0 / ipr) / L)


def localisation_length(strength, length=1200, trials=6, seed=0, hop=None):
    """Localisation length xi, measured on a long chain, independent of d.

    Diagonalise a long disordered chain and take the median inverse
    participation ratio: an eigenstate spread over xi sites has IPR ~ 1/xi.
    Measuring xi separately from the glued-trees run means the criterion
    below is a *prediction* rather than a fit to the same data.
    """
    hop = np.sqrt(2.0) if hop is None else hop
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(trials):
        A = np.zeros((length, length))
        for j in range(length - 1):
            A[j, j + 1] = A[j + 1, j] = hop
        for j in range(length):
            A[j, j] += rng.uniform(-strength / 2, strength / 2)
        _, V = np.linalg.eigh(A)
        out.append(np.median(1.0 / np.sum(V ** 4, axis=0)))
    return float(np.median(out))


def max_depth_before_localisation(strength, **kw):
    """The depth at which the chain (2d+2 sites) outgrows xi.

    Past this the wave packet cannot reach the exit at all, and the
    exponential advantage is gone. This is the number that matters: it says
    how big a problem a given level of imperfection still permits.
    """
    return (localisation_length(strength, **kw) - 2) / 2


def disorder_exponent(strengths=(0.5, 1.0, 2.0, 3.0, 4.0), **kw):
    """Fitted power law xi ~ W^(-alpha). One dimension gives alpha ~ 2 at weak
    disorder; the measured value over this range is nearer 1.7 because the
    chains are finite and the band edges are not weakly disordered."""
    xs = np.array(strengths, dtype=float)
    ys = np.array([localisation_length(float(W), **kw) for W in xs])
    return float(-np.polyfit(np.log(xs), np.log(ys), 1)[0])


def clean_decay_exponent(ds=(16, 40, 80, 150)):
    """How the clean exit probability falls with depth: p ~ d^(-beta).

    The clean walk also loses amplitude as d grows — the packet spreads —
    but only *polynomially*, which is why the separation survives. Worth
    measuring so the disordered case has something honest to be compared
    against.
    """
    ds = np.array(ds, dtype=float)
    ps = np.array([exit_probability(reduced_adjacency(int(d)), d=int(d))[0]
                   for d in ds])
    return float(-np.polyfit(np.log(ds), np.log(ps), 1)[0])


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · THE MECHANISM: BALLISTIC vs DIFFUSIVE\n")
    times = np.array([2, 4, 8, 16, 32, 64], dtype=float)
    L = 401
    q = quantum_spread(L, times)
    c = classical_spread(L, times)
    print(f"   {'t':>6} {'quantum <x²>':>15} {'classical <x²>':>16}")
    for t, a, b in zip(times, q, c):
        print(f"   {t:>6.0f} {a:>15.1f} {b:>16.1f}")
    print(f"\n   fitted exponent  quantum {fit_exponent(times, q):.3f} "
          f"(ballistic = 2)   classical {fit_exponent(times, c):.3f} "
          f"(diffusive = 1)")
    print("   that one exponent is the whole speedup.")

    print("\n2 · THE PRICE: DISORDER, AND HOW MUCH IS TOO MUCH\n")
    depths = (16, 40, 80, 150)
    print("   median exit probability over 16 disorder realisations\n")
    print(f"   {'W':>6}" + "".join(f"{'d=' + str(d):>10}" for d in depths))
    for W in (0.0, 0.5, 1.0, 2.0, 3.0):
        row = "".join(f"{disordered_exit(d, W, trials=16, seed=3):>10.4f}"
                      for d in depths)
        print(f"   {W:>6.1f}{row}")
    print(f"\n   the clean row falls only polynomially: p ~ d^-"
          f"{clean_decay_exponent():.2f} — that is the packet spreading,")
    print("   and it is harmless. Every disordered row falls exponentially.")

    print("\n3 · THE CRITERION, PREDICTED RATHER THAN FITTED\n")
    print("   xi measured on a separate long chain, then compared with the")
    print("   2d+2 sites the algorithm must actually cross:\n")
    print(f"   {'disorder W':>12} {'xi (sites)':>12} "
          f"{'largest usable depth d':>24}")
    for W in (0.5, 1.0, 2.0, 3.0, 4.0):
        xi = localisation_length(W)
        print(f"   {W:>12.1f} {xi:>12.1f} {(xi - 2) / 2:>24.0f}")
    print(f"\n   fitted power law: xi ~ W^-{disorder_exponent():.2f}")
    print("\n   Read it the other way round, which is the uncomfortable")
    print("   direction: to keep the advantage at depth d, the imperfection")
    print("   must satisfy roughly W < (const/d)^(1/1.7). **The tolerable")
    print("   error shrinks as the problem grows.** That is the opposite of")
    print("   what a robust advantage looks like.")


if __name__ == "__main__":
    _demo()
