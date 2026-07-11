"""L3 kill-1 check: does the shallow-depth gradient rate (0.36 bits/k)
persist at depth and in the proportional regime n = 2k?

The L3 escape needs training cost to grow strictly slower than the
4^k-ish surrogate cost. This scan measures Var[dL_k/dtheta] for the
memory-measurable loss L_k = Tr[rho_A^2] across ansatz depths and
subsystem fractions. If deeper/larger drives the training rate up to the
surrogate rate, kill 1 fires and the window closes honestly.

Run: .venv/bin/python hunt/code/rate_persistence.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from swap_loss_bp import _cz, _ry, marginal  # noqa: E402


def ansatz_state(n, theta, depth):
    psi = np.zeros(2 ** n)
    psi[0] = 1.0
    idx = 0
    for _ in range(depth):
        for q in range(n):
            psi = _ry(psi, n, q, theta[idx])
            idx += 1
        for q in range(n):
            psi = _cz(psi, n, q, (q + 1) % n)
    return psi


def grad_var(n, k, depth, samples=100, seed=0):
    rng = np.random.default_rng(seed)
    grads = []
    for _ in range(samples):
        theta = rng.uniform(0, 2 * np.pi, size=depth * n)
        d = 1e-4
        tp, tm = theta.copy(), theta.copy()
        tp[0] += d
        tm[0] -= d

        def L(t):
            rho = marginal(ansatz_state(n, t, depth), n, k)
            return float(np.real(np.trace(rho @ rho)))

        grads.append((L(tp) - L(tm)) / (2 * d))
    return float(np.var(grads))


if __name__ == "__main__":
    print("Var[grad] of L_k = Tr[rho_A^2], proportional regime n = 2k\n")
    print(f"{'depth':>6} " + " ".join(f"k={k:<9}" for k in range(2, 6))
          + "rate (bits/k)")
    for depth in (2, 4, 6):
        vs = [grad_var(2 * k, k, depth, seed=depth) for k in range(2, 6)]
        ks = np.arange(2, 6, dtype=float)
        rate = -np.polyfit(ks, np.log2(vs), 1)[0]
        print(f"{depth:>6} " + " ".join(f"{v:.2e}  " for v in vs)
              + f"{rate:>8.2f}")
    print("\nSurrogate rate for the same loss is ~1.65 bits/k (measured,")
    print("L3 brief) up to ~2 bits/k (4^k marginal reconstruction).")
    print("Kill 1 fires if the training rate reaches the surrogate rate.")
