"""T5 first numerics: the noise face — does noise ever help the device
more than it helps the surrogate?

Known physics, two halves never put on one instrument: (i) noise-induced
barren plateaus — depolarizing noise flattens the landscape
exponentially in circuit volume; (ii) noise makes Pauli-propagation
surrogates CONVERGE FASTER — each noise location damps exactly the
high-weight terms truncation drops. The fifth-face hypothesis: noise
degrades trainability and surrogate cost together, monotonically — no
(p, depth) window where training survives but the surrogate breaks.

Protocol: T3's warm-start setup (n = 8, RY+CZ HEA, 6 layers, eps = 0.1,
H = TFIM+0.4ZZ'), with single-qubit depolarizing (parameter p) after
every gate on every touched qubit. Exact arm = density-matrix
simulation; surrogate arm = truncated backward propagation with the
exact per-location damping factor (1 - 4p/3) on touched terms. GD
trajectories per p in {0, 1e-3, 1e-2, 3e-2}; at fixed step checkpoints
measure: gap closed, gradient norm, and N* (min budget, error <= 0.1,
vs the exact NOISY loss).

PRE-REGISTERED VERDICT (before running at scale):
  - T5 SURVIVES only if some p keeps final gap-closure >= 0.9x the
    noiseless run while N* at matched checkpoints exceeds the
    noiseless N* persistently (noise hurting the surrogate more than
    the device).
  - K1 FIRES (fifth face) if N*(p) is non-increasing in p at every
    checkpoint while trainability (gap closed) is also non-increasing
    — noise helps the classical side, monotonically.

Run: .venv/bin/python hunt/code/t5_noise_face.py    (~15 min)
"""

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from t3_k3_scan import Inst, LADDER  # noqa: E402

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "t5-noise-scan.csv"
N = 8


class NoisyInst(Inst):
    def __init__(self, n, p):
        super().__init__(n)
        self.p = p

    # ----------------------------- exact arm: density matrix ---------
    def _ry_rho(self, rho, q, th):
        n = self.n
        rho = rho.reshape(2 ** (n - 1 - q), 2, 2 ** q, self.dim)
        a, b = rho[:, 0].copy(), rho[:, 1].copy()
        rho[:, 0] = np.cos(th / 2) * a - np.sin(th / 2) * b
        rho[:, 1] = np.sin(th / 2) * a + np.cos(th / 2) * b
        rho = rho.reshape(self.dim, self.dim).conj().T
        rho = rho.reshape(2 ** (n - 1 - q), 2, 2 ** q, self.dim)
        a, b = rho[:, 0].copy(), rho[:, 1].copy()
        rho[:, 0] = np.cos(th / 2) * a - np.sin(th / 2) * b
        rho[:, 1] = np.sin(th / 2) * a + np.cos(th / 2) * b
        return rho.reshape(self.dim, self.dim).conj().T

    def _depol(self, rho, q):
        if self.p == 0:
            return rho
        n = self.n
        sh = (2 ** (n - 1 - q), 2, 2 ** q, 2 ** (n - 1 - q), 2, 2 ** q)
        r = rho.reshape(sh)
        tr = r[:, 0, :, :, 0, :] + r[:, 1, :, :, 1, :]
        mixed = np.zeros_like(r)
        mixed[:, 0, :, :, 0, :] = tr / 2
        mixed[:, 1, :, :, 1, :] = tr / 2
        lam = 4 * self.p / 3
        return ((1 - lam) * r + lam * mixed).reshape(self.dim, self.dim)

    def rho_final(self, params):
        rho = np.zeros((self.dim, self.dim), dtype=complex)
        rho[0, 0] = 1.0
        for g in self.gates:
            if g[0] == "ry":
                rho = self._ry_rho(rho, g[1], params[g[2]])
                rho = self._depol(rho, g[1])
            else:
                i, j = g[1], g[2]
                idx = np.arange(self.dim)
                s = 1 - 2 * (((idx >> i) & 1) & ((idx >> j) & 1))
                rho = rho * np.outer(s, s)
                rho = self._depol(rho, i)
                rho = self._depol(rho, j)
        return rho

    def noisy_loss(self, params):
        rho = self.rho_final(params)
        val = np.sum(self.diag * np.real(np.diag(rho)))
        b = np.arange(self.dim)
        for x, c in self.xflips:
            val += c * np.real(rho[b ^ x, b].sum())
        return float(val)

    # ------------------------- surrogate arm: damped propagation ------
    def noisy_surrogate(self, params, budget):
        from t3_k3_scan import XZ2ID, ID2XZ, _setp
        from t3_warmstart_budget import CZ_TABLE, RY_PARTNER
        lam = 1 - 4 * self.p / 3
        terms = dict(self.terms)

        def damp(terms, qubits):
            if self.p == 0:
                return terms
            out = {}
            for (x, z), c in terms.items():
                f = 1.0
                for q in qubits:
                    if ((x | z) >> q) & 1:
                        f *= lam
                out[(x, z)] = c * f
            return out

        for g in reversed(self.gates):
            if g[0] == "cz":
                i, j = g[1], g[2]
                terms = damp(terms, (i, j))       # noise is after the gate
                new = {}
                for (x, z), c in terms.items():
                    ai = XZ2ID[((x >> i) & 1) + 2 * ((z >> i) & 1)]
                    aj = XZ2ID[((x >> j) & 1) + 2 * ((z >> j) & 1)]
                    bi, bj, s = CZ_TABLE[(ai, aj)]
                    x2, z2 = _setp(x, z, i, ID2XZ[bi])
                    x2, z2 = _setp(x2, z2, j, ID2XZ[bj])
                    new[(x2, z2)] = new.get((x2, z2), 0.0) + s * c
                terms = new
            else:
                q, th = g[1], params[g[2]]
                terms = damp(terms, (q,))
                co, si = np.cos(th), np.sin(th)
                new = {}
                for (x, z), c in terms.items():
                    a = XZ2ID[((x >> q) & 1) + 2 * ((z >> q) & 1)]
                    if a in (0, 2):
                        new[(x, z)] = new.get((x, z), 0.0) + c
                    else:
                        p2, s = RY_PARTNER[a]
                        new[(x, z)] = new.get((x, z), 0.0) + co * c
                        x2, z2 = _setp(x, z, q, ID2XZ[p2])
                        new[(x2, z2)] = new.get((x2, z2), 0.0) + s * si * c
                if budget and len(new) > budget:
                    keep = sorted(new, key=lambda k: -abs(new[k]))[:budget]
                    new = {k: new[k] for k in keep}
                terms = new
        return float(sum(c for (x, z), c in terms.items() if x == 0))

    def noisy_budget(self, params, tol=0.1):
        ex = self.noisy_loss(params)
        for Nb in LADDER:
            if abs(self.noisy_surrogate(params, Nb) - ex) <= tol:
                return Nb
        return None


def descend(inst, th0, steps=60, lr=0.05, h=1e-4, marks=(0, 10, 30, 60)):
    th, out = th0.copy(), {}
    for t in range(steps + 1):
        if t in marks:
            out[t] = th.copy()
        if t == steps:
            break
        g = np.zeros(inst.nparam)
        for k in range(inst.nparam):
            p1, p2 = th.copy(), th.copy()
            p1[k] += h
            p2[k] -= h
            g[k] = (inst.noisy_loss(p1) - inst.noisy_loss(p2)) / (2 * h)
        th = th - lr * g
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(20260717)
    th0 = 0.1 * rng.normal(size=6 * N)
    rows = []
    base_gap = None
    for p in (0.0, 1e-3, 1e-2, 3e-2):
        inst = NoisyInst(N, p)
        L0 = inst.noisy_loss(th0)
        marks = descend(inst, th0)
        print(f"p = {p}:", flush=True)
        for t, th in sorted(marks.items()):
            lo = inst.noisy_loss(th)
            prog = (L0 - lo) / (L0 - inst.emin)
            gn = float(np.linalg.norm(
                [(inst.noisy_loss(np.r_[th[:k], th[k] + 1e-4, th[k+1:]])
                  - inst.noisy_loss(np.r_[th[:k], th[k] - 1e-4, th[k+1:]]))
                 / 2e-4 for k in range(inst.nparam)]))
            nb = inst.noisy_budget(th)
            rows.append(dict(p=p, t=t, loss=lo, progress=prog,
                             grad=gn, nstar=nb))
            print(f"   t={t:>3} loss={lo:>9.4f} progress={prog:>5.2f} "
                  f"|grad|={gn:>7.3f} N*={nb}", flush=True)
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"\nappended {len(rows)} rows to {CSV.name}")
    print("\nPre-registered: fifth face fires if N*(p) and progress(p) are")
    print("both non-increasing in p; T5 survives only if some p keeps")
    print("progress >= 0.9x noiseless while N* exceeds the noiseless N*.")
