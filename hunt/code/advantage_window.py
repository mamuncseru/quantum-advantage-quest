"""The DQI advantage window, computed from verified formulas.

Sources (verified 2026-07-06 against arXiv 2408.08292v5, pp. 4-8; see
hunt/00-verification-log.md):

- Semicircle law (their Eq. 6): with mu = r/p and a decoder correcting
  ell errors on C-perp,

      <s>/m = ( sqrt((ell/m)(1-mu)) + sqrt(mu(1-ell/m)) )^2   if mu <= 1 - ell/m
      <s>/m = 1                                               otherwise.

- OPI + Berlekamp-Massey: substitute ell/m = n/(2p)  (their Section 2).
- Prange baseline for OPI (their Section 11): satisfy n constraints exactly,
  the rest at random  ->  fraction = n/m + mu (1 - n/m); with m = p-1 ~ p
  and mu = 1/2 this is their quoted 1/2 + n/(2p).

The paper's own benchmark numbers are enforced as unit tests — if this file
disagrees with the paper, the tests fail, not the research.
"""

import numpy as np


def dqi_fraction(ell_over_m, mu):
    """Semicircle law: expected satisfied fraction achieved by DQI."""
    ell_over_m = np.asarray(ell_over_m, dtype=float)
    mu = np.asarray(mu, dtype=float)
    inside = (np.sqrt(ell_over_m * (1 - mu))
              + np.sqrt(mu * (1 - ell_over_m))) ** 2
    return np.where(mu <= 1 - ell_over_m, inside, 1.0)


def dqi_opi_fraction(n_over_p, mu):
    """DQI on OPI with the Berlekamp-Massey decoder: ell/m = n/(2p)."""
    return dqi_fraction(np.asarray(n_over_p, dtype=float) / 2.0, mu)


def prange_fraction(n_over_m, mu):
    """Prange / information-set baseline: n constraints exact, rest random."""
    n_over_m = np.asarray(n_over_m, dtype=float)
    return n_over_m + mu * (1 - n_over_m)


def window(n_over_p, mu):
    """DQI-minus-Prange gap on OPI; positive = candidate advantage region."""
    return dqi_opi_fraction(n_over_p, mu) - prange_fraction(n_over_p, mu)


if __name__ == "__main__":
    print("Validation against arXiv 2408.08292v5's own numbers:")
    print(f"  n/p = 1/10, mu = 1/2: DQI    = {float(dqi_opi_fraction(0.1, 0.5)):.4f}"
          f"  (paper: 0.7179)")
    print(f"  n/p = 1/10, mu = 1/2: Prange = {float(prange_fraction(0.1, 0.5)):.4f}"
          f"  (paper: 0.55)")
    print(f"  n/p = 1/2,  mu = 1/2: DQI    = {float(dqi_opi_fraction(0.5, 0.5)):.4f}"
          f"  (paper: 0.9330)")
    print(f"  n/p = 1/2,  mu = 1/2: Prange = {float(prange_fraction(0.5, 0.5)):.4f}"
          f"  (paper: 0.75)")
    x = np.linspace(0.001, 0.999, 999)
    for mu in (0.3, 0.5, 0.7):
        g = window(x, mu)
        i = int(np.argmax(g))
        print(f"  mu = {mu}: max gap {g[i]:+.4f} at n/p = {x[i]:.3f}")
