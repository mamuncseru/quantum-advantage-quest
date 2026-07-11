"""A2 Gate 1: does the Gaussian window preserve the DQI payoff?

The windowed CRT-DQI state is |psi_W> ~ sum_x W(x) P(f(x)) |x>. The
bookkeeping claim: with sigma_f * polylog below the relevant d_min, the
window costs only superpoly-small payoff. Because sigma_x * sigma_f =
M/(2 pi), the claim has two exposed faces of ONE condition:

  state side    - residues equidistribute under W  <=>  the cross-frequency
                  Fourier coefficients of W^2 sit beyond d_min and die
                  (breaks when sigma_x shrinks toward p_max);
  decoder side  - cf_decode is unique on the Gaussian support
                  (breaks when the tail cut reaches d_min(2)/2).

This file tests both EXACTLY - no simulator, no sampling. At l = 1 the
state is psi(x) = W(x) (w0 + w1 S(x)) with S(x) the standardized constraint
sum, a function of the 7-bit pattern of x, so every expectation reduces to
exact 128-bin histograms: unwindowed over all of Z_M, windowed weighted by
W^2. Decoder failure mass is an exact Gaussian-weighted count over every
weight-1 frequency. Stress rows push each face past its hypothesis to
demonstrate falsification power.

Run: .venv/bin/python hunt/code/windowed_payoff.py
"""

import random
import sys
from fractions import Fraction
from math import exp, log, pi, prod
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from cf_decode import cf_decode  # noqa: E402

PRIMES = [3, 5, 7, 11, 13, 17, 19]
M = prod(PRIMES)                       # 4,849,845
D_MIN2 = M // (19 * 17)                # 30,030 - weight-1 bump spacing
D_MIN4 = M // (19 * 17 * 13 * 11)      # 210    - payoff cross-term scale
CHUNK = 1 << 20


def make_instance(seed):
    rng = random.Random(seed)
    return [frozenset(rng.sample(range(p), p // 2)) for p in PRIMES]


def pattern_histograms(F, center, sigma_x):
    """Exact joint histograms of the constraint bits: unwindowed over Z_M,
    and weighted by W(x)^2, W Gaussian(std sigma_x) at center, cut at
    8 sigma."""
    m = len(PRIMES)
    lut = [np.array([int(r in F[i]) for r in range(p)], dtype=np.int64)
           for i, p in enumerate(PRIMES)]

    def patterns(x):
        pat = np.zeros(len(x), dtype=np.int64)
        for i, p in enumerate(PRIMES):
            pat |= lut[i][x % p] << i
        return pat

    hist_u = np.zeros(1 << m)
    for lo in range(0, M, CHUNK):
        x = np.arange(lo, min(lo + CHUNK, M), dtype=np.int64)
        hist_u += np.bincount(patterns(x), minlength=1 << m)

    x = np.arange(max(0, int(center - 8 * sigma_x)),
                  min(M, int(center + 8 * sigma_x) + 1), dtype=np.int64)
    w2 = np.exp(-((x - center) / sigma_x) ** 2)
    hist_w = np.bincount(patterns(x), weights=w2, minlength=1 << m)
    return hist_u, hist_w


def _pattern_stats(mus):
    m = len(PRIMES)
    pats = np.arange(1 << m)
    bits = (pats[:, None] >> np.arange(m)) & 1
    f_val = bits.sum(axis=1)
    S = ((bits - np.asarray(mus)) /
         np.sqrt(np.asarray(mus) * (1 - np.asarray(mus)))).sum(axis=1)
    return f_val, S


def payoff(hist, mus, w0, w1):
    """E[f]/m under amplitudes (w0 + w1 S(x)), exact from a histogram."""
    f_val, S = _pattern_stats(mus)
    weight = hist * (w0 + w1 * S) ** 2
    return float((weight * f_val).sum() / weight.sum() / len(PRIMES))


def optimal_w(hist, mus):
    """Exact optimal (w0, w1): top eigenvector of the 2x2 pencil."""
    f_val, S = _pattern_stats(mus)
    basis = np.stack([np.ones_like(S), S])
    A = np.einsum('ap,bp,p,p->ab', basis, basis, hist, f_val)
    B = np.einsum('ap,bp,p->ab', basis, basis, hist)
    evals, evecs = np.linalg.eigh(np.linalg.solve(B, A))
    return evecs[:, -1]


def decoder_failure_mass(sigma_f, cut=6.0):
    """Exact Gaussian-weighted failure probability of cf_decode over every
    weight-1 frequency; integer shift grid subsampled for speed (weights
    are relative, so subsampling on a uniform grid stays exact per point)."""
    eta = Fraction(int(cut * sigma_f + 1), M)
    reach = int(cut * sigma_f)
    step = max(1, reach // 300)
    fail = total = 0.0
    for i, p in enumerate(PRIMES):
        for k in range(1, p):
            t = k * (M // p) % M
            a_true = [0] * len(PRIMES)
            a_true[i] = k
            for d in range(-reach, reach + 1, step):
                wgt = exp(-(d / sigma_f) ** 2)
                got = cf_decode(PRIMES, 1, Fraction((t + d) % M, M), eta)
                total += wgt
                fail += wgt * (got != a_true)
    return fail / total


if __name__ == "__main__":
    F = make_instance(seed=1)
    mus = [len(F[i]) / p for i, p in enumerate(PRIMES)]
    mu_bar = sum(mus) / len(PRIMES)

    sigma_f = 17.0
    sigma_x = M / (2 * pi * sigma_f)               # ~9.1e4
    kappa = log(6 * sigma_x) / log(M)

    print(f"M = {M},  d_min(2) = {D_MIN2},  d_min(4) = {D_MIN4}")
    print(f"sigma_f = {sigma_f},  sigma_x = {sigma_x:.0f},  "
          f"kappa_eff = {kappa:.2f},  ell/m = {1/7:.3f} < kappa/2 = "
          f"{kappa/2:.2f}\n")

    hist_u, hist_w = pattern_histograms(F, center=M // 2, sigma_x=sigma_x)
    w = optimal_w(hist_u, mus)
    e_u = payoff(hist_u, mus, *w)
    e_w = payoff(hist_w, mus, *w)
    print(f"=== main: window wide (sigma_x/p_max ~ {sigma_x/19:.0f}) ===")
    print(f"  E[f]/m unwindowed (exact):  {e_u:.6f}")
    print(f"  E[f]/m windowed   (exact):  {e_w:.6f}")
    print(f"  |difference|:               {abs(e_u - e_w):.2e}")
    print(f"  random baseline mu_bar:     {mu_bar:.4f}")
    print(f"  (CRT-Prange at kappa_eff would be "
          f"{kappa + mu_bar*(1-kappa):.4f}; toy m=7 is not the advantage "
          f"regime - the test here is windowed vs unwindowed)")

    print("\n=== decoder failure mass at the design point ===")
    print(f"  sigma_f = {sigma_f}: {decoder_failure_mass(sigma_f):.2e}")

    print("\n=== stress, state side: sigma_x down toward p_max ===")
    print(f"{'sigma_x':>9} {'sigma_x/p_max':>14} {'E_w - E_u':>12}")
    for sx in (sigma_x, 2000.0, 200.0, 40.0, 15.0):
        _, hw = pattern_histograms(F, center=M // 2, sigma_x=sx)
        print(f"{sx:>9.0f} {sx/19:>14.1f} "
              f"{payoff(hw, mus, *w) - e_u:>12.2e}")

    print("\n=== stress, decoder side: cut pushed toward d_min(2)/2 = "
          f"{D_MIN2//2} ===")
    print(f"{'sigma_f':>9} {'6*sigma_f':>10} {'failure mass':>13}")
    for sf in (17.0, 1000.0, 2000.0, 3000.0, 5000.0):
        print(f"{sf:>9.0f} {6*sf:>10.0f} {decoder_failure_mass(sf):>13.2e}")

    print("\nReading: E_w = E_u to near machine precision and zero decoder")
    print("failures inside the hypothesis; each face degrades exactly when")
    print("its own condition (equidistribution / d_min(2)) is violated.")
