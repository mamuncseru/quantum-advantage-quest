"""A2 bookkeeping at ell = 2: the lemma's mechanism is ell-generic; this
replicates the exact ell=1 validation one degree up.

State: psi = W(x) (w0 + w1 S(x) + w2 Q(x)), with S the standardized
constraint sum (shell 1) and Q = sum_{i<j} g_i g_j (shell 2) - still a
function of the 7-bit constraint pattern, so the exact 128-bin histogram
method applies unchanged. Predicted thresholds move to
d_min(2l+1) = d_min(5) = M / (19*17*13*11*7) = 15 (state side) and
d_min(2l)/2 = d_min(4)/2 = 52 (decoder side, ell=2 lists).

Run: .venv/bin/python hunt/code/windowed_payoff_l2.py
"""

import sys
from fractions import Fraction
from math import exp, pi
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from cf_decode import cf_decode  # noqa: E402
from windowed_payoff import (M, PRIMES, make_instance,
                             pattern_histograms)  # noqa: E402

D_MIN4 = M // (19 * 17 * 13 * 11)          # 105
D_MIN5 = M // (19 * 17 * 13 * 11 * 7)      # 15


def _stats(mus):
    m = len(PRIMES)
    pats = np.arange(1 << m)
    bits = (pats[:, None] >> np.arange(m)) & 1
    g = (bits - np.asarray(mus)) / np.sqrt(
        np.asarray(mus) * (1 - np.asarray(mus)))
    S = g.sum(axis=1)
    Q = (S ** 2 - (g ** 2).sum(axis=1)) / 2          # sum_{i<j} g_i g_j
    return bits.sum(axis=1), np.stack([np.ones_like(S), S, Q])


def payoff_l2(hist, mus, w):
    f_val, basis = _stats(mus)
    weight = hist * (w @ basis) ** 2
    return float((weight * f_val).sum() / weight.sum() / len(PRIMES))


def optimal_w_l2(hist, mus):
    f_val, basis = _stats(mus)
    A = np.einsum('ap,bp,p,p->ab', basis, basis, hist, f_val)
    B = np.einsum('ap,bp,p->ab', basis, basis, hist)
    evals, evecs = np.linalg.eigh(np.linalg.solve(B, A))
    return evecs[:, -1]


def decoder_failure_mass_l2(sigma_f, cut=6.0):
    """Exact Gaussian-weighted cf_decode failure over every weight-2
    frequency (subsampled shift grid)."""
    eta = Fraction(int(cut * sigma_f + 1), M)
    reach = int(cut * sigma_f)
    step = max(1, reach // 120)
    fail = total = 0.0
    for i in range(len(PRIMES)):
        for j in range(i + 1, len(PRIMES)):
            pi_, pj = PRIMES[i], PRIMES[j]
            for ki in (1, pi_ // 2):
                for kj in (1, pj // 2):
                    t = (ki * (M // pi_) + kj * (M // pj)) % M
                    a_true = [0] * len(PRIMES)
                    a_true[i], a_true[j] = ki, kj
                    for d in range(-reach, reach + 1, step):
                        wgt = exp(-(d / sigma_f) ** 2)
                        got = cf_decode(PRIMES, 2,
                                        Fraction((t + d) % M, M), eta)
                        total += wgt
                        fail += wgt * (got != a_true)
    return fail / total


if __name__ == "__main__":
    F = make_instance(seed=1)
    mus = [len(F[i]) / p for i, p in enumerate(PRIMES)]

    sigma_f = 1.2
    sigma_x = M / (2 * pi * sigma_f)
    print(f"ell = 2:  d_min(4) = {D_MIN4},  d_min(5) = {D_MIN5},  "
          f"sigma_f = {sigma_f}\n")

    hist_u, hist_w = pattern_histograms(F, center=M // 2, sigma_x=sigma_x)
    w = optimal_w_l2(hist_u, mus)
    e_u = payoff_l2(hist_u, mus, w)
    e_w = payoff_l2(hist_w, mus, w)
    print(f"E[f]/m unwindowed: {e_u:.6f}   windowed: {e_w:.6f}   "
          f"|diff| = {abs(e_u - e_w):.2e}")

    print("\nstate-side stress (threshold predicted at 3 sigma_f ~ "
          f"d_min(5) = {D_MIN5}):")
    print(f"{'sigma_f':>8} {'3*sigma_f':>10} {'E_w - E_u':>12}")
    for sf in (1.2, 5.0, 15.0):
        _, hw = pattern_histograms(F, center=M // 2,
                                   sigma_x=M / (2 * pi * sf))
        print(f"{sf:>8.1f} {3*sf:>10.1f} "
              f"{payoff_l2(hw, mus, w) - e_u:>12.2e}")

    print("\ndecoder-side stress (wall predicted at cut ~ d_min(4)/2 = "
          f"{D_MIN4/2:.0f}):")
    print(f"{'sigma_f':>8} {'6*sigma_f':>10} {'failure mass':>13}")
    for sf in (1.2, 8.0, 20.0):
        print(f"{sf:>8.1f} {6*sf:>10.1f} "
              f"{decoder_failure_mass_l2(sf):>13.2e}")
