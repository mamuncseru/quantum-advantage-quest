"""L5 tension scan: does any temperature give BOTH slow mixing (L1's
advantage regime) AND weight-concentrated Pauli spectrum (L5's noise
robustness)? If the two windows are disjoint in beta, L1's advantage is
NISQ-fragile; if they overlap, physical data is the shield after all.

Proxies, both computed exactly from the spectrum / state (n<=7):
  robustness  = gamma* (critical storage noise for swap-test bias eps),
                large when the Pauli spectrum is weight-concentrated;
  mixing-slow = 1 / Davies gap (large = slow mixing = L1 advantage),
                capped at n<=6 for the 4^n superoperator.

We sweep beta and look for a co-window. This is the kill-2 check of the
L5 brief made quantitative.

Run: .venv/bin/python hunt/code/l5_tension.py
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from qsim import X, Y, Z  # noqa: E402
from noise_threshold import gamma_star, pauli_weight_spectrum  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "davies", ROOT / "predecessors/12-gibbs-lindblad/davies.py")
davies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(davies)

N, EPS = 5, 0.05


def build_H(n, seed, h=1.0):
    rng = np.random.default_rng(seed)
    field = rng.uniform(-1, 1, size=n)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            H += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        H += h * field[i] * davies.site_op(Z, i, n)
    return H


def gibbs_from_H(H, beta):
    w, v = np.linalg.eigh(H)
    e = np.exp(-beta * (w - w.min()))
    return (v * (e / e.sum())) @ v.conj().T


def davies_gap(H, n, beta):
    coup = [davies.site_op(X, i, n) for i in range(n)] + \
           [davies.site_op(Y, i, n) for i in range(n)]
    return davies.spectral_gap(davies.davies_superoperator(H, coup, beta))


if __name__ == "__main__":
    H = build_H(N, seed=N)
    print(f"L5 tension scan, n={N}, disordered Heisenberg, eps={EPS}\n")
    print(f"{'beta':>6} {'gamma* (robust)':>16} {'Davies gap':>11} "
          f"{'1/gap (slow-mix)':>17} {'mean Pauli wt':>14}")
    for beta in (0.25, 0.5, 1.0, 2.0, 4.0):
        rho = gibbs_from_H(H, beta)
        spec_w = pauli_weight_spectrum(rho, N)
        gstar = gamma_star(spec_w, EPS)
        gap = davies_gap(H, N, beta)
        w = np.arange(N + 1)
        mwt = float((spec_w[1:] * w[1:]).sum() / spec_w[1:].sum())
        print(f"{beta:>6.2f} {gstar:>16.4f} {gap:>11.4f} "
              f"{1/gap:>17.3f} {mwt:>14.2f}", flush=True)
    print("\nRead: robustness wants gamma* large (weight-concentrated,")
    print("favored at LOW beta / high T); L1 advantage wants 1/gap large")
    print("(slow mixing). If gamma* falls monotonically as 1/gap rises,")
    print("the windows are DISJOINT and L1 is NISQ-fragile; a non-monotone")
    print("co-window would be the (surprising) good news.")
