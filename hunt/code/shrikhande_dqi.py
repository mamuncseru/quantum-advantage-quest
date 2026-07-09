"""Doob K3 resolution: does Doob-DQI beat the best classical baseline for
Shrikhande-radial pair predicates, or only replicate Hamming?

Two exact computations on the 16-element Shrikhande scheme, plus a brute-force
max-LinSAT sanity check. Resolves the K3 red flag of
hunt/notes/A3-product-theorem.md rigorously.

Key structural fact (verified in that note): Doob D(m,n) has the SAME
intersection array / Jacobi matrix as H(2m+n,4). The DQI semicircle (Eq 6 of
2408.08292, verified in hunt/code/advantage_window.py) depends ONLY on the
per-constraint density mu and the decoder radius l/m — not on the alphabet.
So DQI-on-Doob = DQI-on-Hamming at matched (mu, l/m). The only thing that can
differ is the CLASSICAL baseline. We show it is strictly stronger on Doob.

Run: .venv/bin/python hunt/code/shrikhande_dqi.py
"""

import sys
from collections import deque
from itertools import product
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from product_schemes import shrikhande  # noqa: E402

SHRIK_CONN = [(1, 0), (3, 0), (0, 1), (0, 3), (1, 1), (3, 3)]
Z4 = [(a, b) for a in range(4) for b in range(4)]


def shells():
    """Shrikhande distance shells from (0,0): sizes 1, 6, 9."""
    A = shrikhande()
    idx = {e: i for i, e in enumerate(Z4)}
    dist = {0: 0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in np.nonzero(A[u])[0]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(int(v))
    sh = {0: [], 1: [], 2: []}
    for e in Z4:
        sh[dist[idx[e]]].append(e)
    return sh


def radial_predicate(g0, g1, g2):
    """Indicator support of a Shrikhande-radial predicate (values on shells)."""
    sh = shells()
    supp = set()
    for d, gd in enumerate((g0, g1, g2)):
        if gd:
            supp.update(sh[d])
    return supp


def density(supp):
    return len(supp) / 16.0


def conditional_bias(supp):
    """max over (form, value) of P(pair in supp | that form pinned to value).
    This is the lever the predicate-aware classical attacker pulls."""
    best = 0.0
    best_desc = None
    for form in (0, 1):                       # pin u (form 0) or v (form 1)
        for val in range(4):
            hits = sum(1 for e in Z4 if e[form] == val and e in supp)
            p = hits / 4.0
            if p > best:
                best, best_desc = p, (form, val)
    return best, best_desc


def prange_slopes(supp):
    """Two classical satisfied-fraction slopes vs budget tau = (#pinned forms)/m':
       - array-matched: pin BOTH forms of a block (2 units) to fully satisfy
       - predicate-aware: pin ONE form (1 unit) exploiting conditional bias
    Returns (mu, array_slope_per_unit, aware_slope_per_unit)."""
    mu = density(supp)
    bias, _ = conditional_bias(supp)
    # array-matched: 2 units buy (1 - mu) marginal  -> per unit (1-mu)/2
    array_slope = (1 - mu) / 2
    # predicate-aware: 1 unit buys (bias - mu) marginal -> per unit (bias - mu)
    aware_slope = bias - mu
    return mu, array_slope, aware_slope


def dqi_semicircle(mu, l_over_m):
    """Universal DQI payoff (Eq 6). Alphabet-independent."""
    if mu <= 1 - l_over_m:
        return (np.sqrt(l_over_m * (1 - mu))
                + np.sqrt(mu * (1 - l_over_m))) ** 2
    return 1.0


# ---------- brute-force max-Shrikhande-LinSAT sanity check ----------

def random_instance(n, mprime, supp, seed):
    """Affine max-LinSAT: constraint i satisfied iff the pair lands in the
    predicate support SHIFTED by a random center (c1_i, c2_i). Random centers
    are essential — without them x=0 trivially satisfies every homogeneous
    constraint (the pair (0,0) is in every radius ball)."""
    rng = np.random.default_rng(seed)
    B1 = rng.integers(0, 4, size=(mprime, n))
    B2 = rng.integers(0, 4, size=(mprime, n))
    C1 = rng.integers(0, 4, size=mprime)
    C2 = rng.integers(0, 4, size=mprime)
    return B1, B2, C1, C2


def satisfied(x, inst, supp):
    B1, B2, C1, C2 = inst
    u = (B1 @ x - C1) % 4
    v = (B2 @ x - C2) % 4
    return sum(1 for a, b in zip(u, v) if (int(a), int(b)) in supp)


def brute_optimum(n, inst, supp):
    best = 0
    for x in product(range(4), repeat=n):
        best = max(best, satisfied(np.array(x), inst, supp))
    return best


def classical_strong(n, inst, supp, restarts=200, seed=0):
    """Strong poly-time baseline: random restart + greedy coordinate local
    search (flip each x_i to its best value, iterate to a local optimum).
    This is the fair 'symmetric effort' classical opponent."""
    rng = np.random.default_rng(seed)
    best = 0
    for _ in range(restarts):
        x = rng.integers(0, 4, size=n)
        improved = True
        while improved:
            improved = False
            for i in range(n):
                cur = satisfied(x, inst, supp)
                for val in range(4):
                    if val == x[i]:
                        continue
                    x[i], old = val, x[i]
                    if satisfied(x, inst, supp) > cur:
                        improved = True
                        break
                    x[i] = old
        best = max(best, satisfied(x, inst, supp))
    return best


if __name__ == "__main__":
    print("Shrikhande shells (sizes):",
          {d: len(v) for d, v in shells().items()})
    print()

    print("=== The g = 1_{B1} predicate (radius-1 ball, mu = 7/16) ===")
    supp = radial_predicate(1, 1, 0)
    mu = density(supp)
    bias, desc = conditional_bias(supp)
    print(f"  support size {len(supp)}, mu = {mu:.4f} = {len(supp)}/16")
    print(f"  conditional bias: pin form {desc[0]} to {desc[1]} "
          f"-> P(sat) = {bias:.4f} = {round(bias*4)}/4")
    mu, arr, aware = prange_slopes(supp)
    print(f"  array-matched Prange slope  = {arr:.4f} = {round(arr*32)}/32 per unit")
    print(f"  predicate-aware slope       = {aware:.4f} = {round(aware*32)}/32 per unit")
    print(f"  predicate-aware STRICTLY stronger: {aware > arr}")
    print()

    print("=== DQI semicircle at mu = 7/16 (alphabet-independent) ===")
    for lm in (0.05, 0.1, 0.2):
        print(f"  l/m = {lm}: DQI = {dqi_semicircle(mu, lm):.4f}")
    print("  (identical to Hamming DQI at the same mu, l/m — Doob's Jacobi")
    print("   equals H(2m+n,4)'s, and Eq 6 has no alphabet dependence)")
    print()

    print("=== brute-force max-LinSAT, OVERCONSTRAINED (hard) regime ===")
    print("  optimum < 1 here; does strong poly-time classical track it?")
    for (n, mp) in ((7, 40), (7, 60), (8, 60)):
        gaps = []
        for seed in range(5):
            inst = random_instance(n, mp, supp, seed=seed)
            opt = brute_optimum(n, inst, supp)
            cls = classical_strong(n, inst, supp, seed=seed + 10)
            gaps.append((opt, cls))
        opt_m = np.mean([g[0] for g in gaps]) / mp
        cls_m = np.mean([g[1] for g in gaps]) / mp
        print(f"  n={n}, m'={mp}: opt={opt_m:.3f}, strong classical={cls_m:.3f}, "
              f"gap={opt_m - cls_m:.3f}  (random={mu:.3f})")
