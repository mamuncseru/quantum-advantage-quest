"""L5 first numerics: does PHYSICAL structure make memory advantages
noise-robust?

Noisy Quantum Learning Theory (arXiv 2512.10929) proves the two-copy
purity advantage collapses under local depolarizing memory noise for
worst-case states, and exhibits one exotic structure that restores it.
L5's conjecture: THERMAL structure restores it too. Mechanism: per-qubit
depolarizing at rate gamma damages the Pauli spectrum sector of weight w
by (1-gamma)^{2w},

    Tr[(L_g rho)^2] = 2^{-n} sum_a (1-gamma)^{2|a|} Tr[W_a rho]^2 ,

so states with weight-concentrated spectra (local Gibbs states) lose
O(gamma) bias while states with typical-weight spectra (Haar-like) lose
exp(-c gamma n). We compute the critical storage noise gamma*(n) where
the swap-test bias hits eps, exactly, for Gibbs vs Haar states.

Run: .venv/bin/python hunt/code/noise_threshold.py
"""

import sys
from itertools import product
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from memory_purity import gibbs_state  # noqa: E402

PAULI = [np.eye(2, dtype=complex),
         np.array([[0, 1], [1, 0]], dtype=complex),
         np.array([[0, -1j], [1j, 0]]),
         np.diag([1.0, -1.0]).astype(complex)]


def pauli_weight_spectrum(rho, n):
    """s[w] = 2^{-n} sum_{|a|=w} Tr[W_a rho]^2 (so sum_w s[w] = Tr rho^2)."""
    s = np.zeros(n + 1)
    for a in product(range(4), repeat=n):
        W = PAULI[a[0]]
        for p in a[1:]:
            W = np.kron(W, PAULI[p])
        w = sum(1 for p in a if p)
        s[w] += float(np.real(np.trace(W @ rho))) ** 2
    return s / 2 ** n


def noisy_purity(spec, gamma):
    w = np.arange(len(spec))
    return float((spec * (1 - gamma) ** (2 * w)).sum())


def gamma_star(spec, eps):
    """Largest per-qubit storage noise with swap-test bias <= eps."""
    purity = spec.sum()
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if purity - noisy_purity(spec, mid) <= eps:
            lo = mid
        else:
            hi = mid
    return lo


def haar_state_dm(n, rng):
    v = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
    v /= np.linalg.norm(v)
    return np.outer(v, v.conj())


if __name__ == "__main__":
    EPS = 0.05
    rng = np.random.default_rng(5)
    print("Critical storage-noise rate gamma* (swap-test bias = "
          f"{EPS}) - Gibbs vs Haar\n")
    print(f"{'n':>3} {'gamma* Gibbs':>13} {'gamma* Haar':>12} "
          f"{'mean wt Gibbs':>14} {'mean wt Haar':>13}")
    gs, hs, ns = [], [], []
    for n in range(2, 8):
        spec_g = pauli_weight_spectrum(gibbs_state(n, seed=n), n)
        spec_h = pauli_weight_spectrum(haar_state_dm(n, rng), n)
        w = np.arange(n + 1)
        mw_g = float((spec_g[1:] * w[1:]).sum() / spec_g[1:].sum())
        mw_h = float((spec_h[1:] * w[1:]).sum() / spec_h[1:].sum())
        g_g, g_h = gamma_star(spec_g, EPS), gamma_star(spec_h, EPS)
        ns.append(n)
        gs.append(g_g)
        hs.append(g_h)
        print(f"{n:>3} {g_g:>13.4f} {g_h:>12.4f} {mw_g:>14.2f} "
              f"{mw_h:>13.2f}")

    fit_g = np.polyfit(np.log(ns), np.log(gs), 1)[0]
    fit_h = np.polyfit(np.log(ns), np.log(hs), 1)[0]
    print(f"\ngamma* scaling exponents (log-log slope): "
          f"Gibbs {fit_g:.2f}, Haar {fit_h:.2f}")
    print("Haar-like states: gamma* shrinks with n (the 2512.10929")
    print("collapse); if the Gibbs exponent is materially flatter, thermal")
    print("structure buys noise robustness - L1's advantage would be")
    print("NISQ-tolerant BECAUSE its data is physical.")
