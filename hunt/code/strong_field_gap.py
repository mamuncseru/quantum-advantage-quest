"""C1 follow-up: does the Davies mixing gap stay OPEN at strong disordered
field as n grows? The first atlas found the interesting regime is strong
random field (uniform re-productizes, random stays entangled); the mechanism
needs the quantum sampler to keep mixing there. This tests the gap-vs-n.

Davies superoperator is 4^n x 4^n, so n is capped at 6 for dense eig.
Run: .venv/bin/python hunt/code/strong_field_gap.py
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

BETA, H = 1.0, 8.0            # intermediate temperature, STRONG field


def gap_at(n, seed):
    rng = np.random.default_rng(seed)
    field = rng.uniform(-1, 1, size=n)
    Hm = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            Hm += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        Hm += H * field[i] * davies.site_op(Z, i, n)
    coup = [davies.site_op(X, i, n) for i in range(n)] + \
           [davies.site_op(Y, i, n) for i in range(n)]
    return davies.spectral_gap(davies.davies_superoperator(Hm, coup, BETA))


if __name__ == "__main__":
    print(f"Davies gap at strong disordered field (beta={BETA}, h={H}):\n")
    print(f"{'n':>3} {'seeds':>6} {'mean gap':>10} {'min gap':>9} {'std':>8}")
    rows = []
    for n in (3, 4, 5, 6):
        reps = 8 if n <= 5 else 4
        gaps = [gap_at(n, s) for s in range(reps)]
        rows.append((n, np.mean(gaps), np.min(gaps), np.std(gaps)))
        print(f"{n:>3} {reps:>6} {np.mean(gaps):>10.4f} {np.min(gaps):>9.4f} "
              f"{np.std(gaps):>8.4f}", flush=True)
    with open(ROOT / "hunt" / "strongfield-gap.csv", "w") as fh:
        fh.write("n,mean_gap,min_gap,std\n")
        for r in rows:
            fh.write(f"{r[0]},{r[1]:.6f},{r[2]:.6f},{r[3]:.6f}\n")
    print("\ndone — if min gap stays bounded away from 0, the mixer survives.")
