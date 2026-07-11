"""L1 first numerics: two-copy vs single-copy cost of Renyi-2 estimation
on Gibbs states of the disordered Heisenberg chain (C1's model).

Task: estimate purity Tr(rho_beta^2) to +-eps.

  two-copy (nature's copies + swap test): Bernoulli with p = (1+P)/2,
      N = 4 p (1-p) / eps^2   -- independent of n.
  single-copy (random-Pauli classical shadows, U-statistic estimator):
      variance grows exponentially with n for generic states.
  single-copy AAKS path: poly samples learn H, but extracting the purity
      from (H, beta) is a partition-function computation -- the point of
      the L1 frame: on physical data the separation is COMPUTATIONAL.

Everything except the shadow sampling itself is exact (dense rho, exact
outcome distributions per measurement basis, memoized).

Run: .venv/bin/python hunt/code/memory_purity.py
"""

import importlib.util
import sys
from functools import reduce
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from qsim import X, Y, Z  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "davies", ROOT / "predecessors/12-gibbs-lindblad/davies.py")
davies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(davies)

BETA, H_FIELD = 1.0, 1.0

# single-site rotations to the Z eigenbasis for measuring X, Y, Z
_H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
_SDG = np.diag([1.0, -1.0j])
ROT = {0: _H, 1: _H @ _SDG, 2: np.eye(2)}          # X, Y, Z


def gibbs_state(n, seed):
    rng = np.random.default_rng(seed)
    field = rng.uniform(-1, 1, size=n)
    Hm = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            Hm += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        Hm += H_FIELD * field[i] * davies.site_op(Z, i, n)
    w, v = np.linalg.eigh(Hm)
    e = np.exp(-BETA * (w - w.min()))
    return (v * (e / e.sum())) @ v.conj().T


def swap_test_samples(purity, eps):
    p = (1 + purity) / 2
    return 4 * p * (1 - p) / eps ** 2


class ShadowSampler:
    """Random-Pauli shadows with exact per-basis outcome distributions."""

    def __init__(self, rho, rng):
        self.rho = rho
        self.n = int(np.log2(rho.shape[0]))
        self.rng = rng
        self._dist = {}

    def _distribution(self, basis):
        if basis not in self._dist:
            U = reduce(np.kron, [ROT[b] for b in basis])
            self._dist[basis] = np.maximum(
                np.real(np.einsum('sj,jk,sk->s', U, self.rho, U.conj())), 0)
        return self._dist[basis]

    def snapshots(self, N):
        bases = self.rng.integers(0, 3, size=(N, self.n))
        outs = np.empty((N, self.n), dtype=np.int64)
        for i in range(N):
            b = tuple(int(x) for x in bases[i])
            d = self._distribution(b)
            s = self.rng.choice(len(d), p=d / d.sum())
            outs[i] = [(s >> (self.n - 1 - j)) & 1 for j in range(self.n)]
        return bases, outs


def shadow_purity(bases, outs):
    """U-statistic over snapshot pairs; per-site pair traces are
    5 (same basis, same outcome), -4 (same basis, opposite), 1/2 (else)."""
    N = len(bases)
    same_b = bases[:, None, :] == bases[None, :, :]
    same_o = outs[:, None, :] == outs[None, :, :]
    site = np.where(same_b, np.where(same_o, 5.0, -4.0), 0.5)
    prod = site.prod(axis=2)
    return (prod.sum() - np.trace(prod)) / (N * (N - 1))


def shadow_cost(rho, eps, N=600, reps=20, seed=0):
    """Empirical samples-to-eps for the shadow estimator: measure the
    estimator std at N snapshots, scale by the U-statistic 1/N rate."""
    rng = np.random.default_rng(seed)
    sampler = ShadowSampler(rho, rng)
    vals = [shadow_purity(*sampler.snapshots(N)) for _ in range(reps)]
    std = float(np.std(vals))
    return N * (std / eps) ** 2, float(np.mean(vals)), std


if __name__ == "__main__":
    EPS = 0.05
    print("Renyi-2 of disordered-Heisenberg Gibbs states "
          f"(beta={BETA}, h={H_FIELD}), eps={EPS}\n")
    print(f"{'n':>3} {'purity':>8} {'swap N':>8} {'shadow N':>12} "
          f"{'ratio':>10} {'mean dev +- SE':>16}")
    rows = []
    for n in range(2, 9):
        rho = gibbs_state(n, seed=n)
        P = float(np.real(np.trace(rho @ rho)))
        n_swap = swap_test_samples(P, EPS)
        n_shad, mean, std = shadow_cost(rho, EPS, seed=n)
        rows.append((n, n_shad))
        # the U-statistic is exactly unbiased; at large n its distribution
        # is heavy-tailed (rare same-basis pairs contribute 5^n spikes), so
        # the mean deviation must be read against the standard error
        print(f"{n:>3} {P:>8.4f} {n_swap:>8.0f} {n_shad:>12.0f} "
              f"{n_shad/n_swap:>10.1f} {mean - P:>+9.3f} +- "
              f"{std/np.sqrt(20):.3f}")

    ns = np.array([r[0] for r in rows], dtype=float)
    slope = np.polyfit(ns, np.log2([r[1] for r in rows]), 1)[0]
    print(f"\nshadow cost doubling rate: {slope:.2f} bits per qubit "
          f"(exponential); swap cost is flat by construction.")
    print("AAKS path: poly samples learn H single-copy - but turning")
    print("(H, beta) into the purity is a partition-function computation.")
    print("On physical data the memory advantage is computational, not")
    print("sample-theoretic: rebuilding rho_beta to swap against costs")
    print("exactly the Gibbs-preparation/mixing time (ground C).")
