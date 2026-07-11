"""L8 first numerics: the telescoped free-energy estimator - what fresh
Gibbs copies at a SCHEDULE of temperatures buy.

Entropy/free energy need log Z. Nature hands out copies at ONE beta;
a learner that can REBUILD (fast mixing) can produce copies along a
schedule beta_0=0 < ... < beta_K = beta and telescope

    Z(b_{i+1})/Z(b_i) = E_{rho_{b_i}}[ exp(-(b_{i+1}-b_i) H) ],

each factor estimated by measuring H-eigenvalues on fresh copies. The
estimator is useful iff each factor's relative variance is O(1). This
file computes those variances EXACTLY from the spectrum: a single jump
(K=1) has exponentially bad relative variance, while K ~ beta * ||H||
steps keep every factor tame - so the rebuild dividend turns
free-energy/entropy estimation poly. Nature's fixed-beta copies cannot
telescope: the dividend belongs to the preparer. (L1's converse: FAST
mixing is the advantage here.)

Run: .venv/bin/python hunt/code/ratio_telescope.py
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from qsim import X, Y, Z  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "davies", ROOT / "predecessors/12-gibbs-lindblad/davies.py")
davies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(davies)

N, BETA = 5, 2.0


def spectrum(n, seed):
    rng = np.random.default_rng(seed)
    field = rng.uniform(-1, 1, size=n)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            H += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        H += field[i] * davies.site_op(Z, i, n)
    return np.linalg.eigvalsh(H)


def factor_rel_var(w, b_lo, b_hi):
    """Relative variance of exp(-(b_hi-b_lo) H) under rho_{b_lo}, exact."""
    p = np.exp(-b_lo * (w - w.min()))
    p /= p.sum()
    x = np.exp(-(b_hi - b_lo) * (w - w.min()))
    mean = float((p * x).sum())
    return float((p * x ** 2).sum()) / mean ** 2 - 1.0


if __name__ == "__main__":
    w = spectrum(N, seed=3)
    print(f"n = {N}, beta = {BETA}, spectral width = {w.max()-w.min():.2f}\n")
    print(f"{'K steps':>8} {'max factor rel-var':>19} "
          f"{'total rel-var (sum)':>20}")
    for K in (1, 2, 4, 8, 16, 32):
        bs = np.linspace(0, BETA, K + 1)
        rvs = [factor_rel_var(w, bs[i], bs[i + 1]) for i in range(K)]
        print(f"{K:>8} {max(rvs):>19.3f} {sum(rvs):>20.3f}")
    print("\nSingle jump: exponentially bad; a modest schedule tames every")
    print("factor. Requirement: fresh copies at ALL schedule temperatures -")
    print("i.e. a preparer, not nature's fixed-beta samples. Fast mixing is")
    print("an ADVANTAGE source for entropy tasks: the converse of L1.")
