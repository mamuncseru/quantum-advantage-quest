"""T3/K3: the decisive scaling scan — surrogate budget at MATCHED
training progress vs system size.

Protocol (fixed by the T3 brief): RY+CZ hardware-efficient ansatz,
6 layers, warm start eps = 0.1; H = open-chain TFIM(g=1) +
0.4 sum Z_i Z_{i+2}; gradient-descent trajectory per n; at the first
crossings of progress p in {0.5, 0.9, 0.95} (fraction of the initial
energy gap closed), measure N* = minimal Pauli-term budget with loss
error <= 0.0125*n (the n=8 brief tolerance, scaled extensively).

PRE-REGISTERED VERDICT (written before running at scale):
  Fit log2 N*(p=0.9) against n (exponential model, slope alpha
  bits/qubit) and against log2 n (polynomial model, degree k).
  - K3 FIRES (poly; the warm-start face closes) if the polynomial fit
    is at least as good (R^2) and the exponential fit gives
    alpha < 0.5 bits/qubit.
  - T3 SURVIVES if alpha >= 1.0 with R^2 > 0.9 while gradient norms at
    the same checkpoints stay >= 1/poly (non-collapsing).
  - Else inconclusive: extend n or bring theory.

Run: .venv/bin/python hunt/code/t3_k3_scan.py     (~20 min; CSV to
hunt/t3-k3-scan.csv)
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).parent))
from t3_warmstart_budget import CZ_TABLE, RY_PARTNER  # noqa: E402

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "t3-k3-scan.csv"
LAYERS = 6
XZ2ID = {0: 0, 1: 1, 2: 3, 3: 2}          # (xbit + 2*zbit) -> pauli id
ID2XZ = {0: 0, 1: 1, 3: 2, 2: 3}


class Inst:
    def __init__(self, n):
        self.n, self.dim = n, 2 ** n
        self.gates = []
        k = 0
        for _ in range(LAYERS):
            for q in range(n):
                self.gates.append(("ry", q, k))
                k += 1
            for q in range(0, n - 1, 2):
                self.gates.append(("cz", q, q + 1))
            for q in range(1, n - 1, 2):
                self.gates.append(("cz", q, q + 1))
        self.nparam = k
        self.terms = {}
        for i in range(n - 1):
            self.terms[(0, (1 << i) | (1 << (i + 1)))] = 1.0
        for i in range(n):
            self.terms[((1 << i), 0)] = 1.0
        for i in range(n - 2):
            key = (0, (1 << i) | (1 << (i + 2)))
            self.terms[key] = self.terms.get(key, 0.0) + 0.4
        b = np.arange(self.dim)
        self.diag = np.zeros(self.dim)
        self.xflips = []
        for (x, z), c in self.terms.items():
            if x == 0:
                # bitwise_count returns uint8 — cast BEFORE the sign
                # arithmetic or -1 underflows to 255
                odd = np.bitwise_count(b & z).astype(np.int64) & 1
                self.diag += c * (1 - 2 * odd)
            else:
                self.xflips.append((x, c))
        op = LinearOperator((self.dim, self.dim), matvec=self._hv,
                            dtype=float)
        self.emin = float(eigsh(op, k=1, which="SA")[0][0])

    def _hv(self, v):
        out = self.diag * v
        b = np.arange(self.dim)
        for x, c in self.xflips:
            out = out + c * v[b ^ x]
        return out

    def state(self, params):
        v = np.zeros(self.dim, dtype=complex)
        v[0] = 1.0
        n = self.n
        for g in self.gates:
            if g[0] == "ry":
                q, th = g[1], params[g[2]]
                v = v.reshape(2 ** (n - 1 - q), 2, 2 ** q)
                a, bb = v[:, 0].copy(), v[:, 1].copy()
                v[:, 0] = np.cos(th / 2) * a - np.sin(th / 2) * bb
                v[:, 1] = np.sin(th / 2) * a + np.cos(th / 2) * bb
                v = v.reshape(-1)
            else:
                i, j = g[1], g[2]
                idx = np.arange(self.dim)
                mask = ((idx >> i) & 1) & ((idx >> j) & 1)
                v = v * (1 - 2 * mask)
        return v

    def exact_loss(self, params):
        v = self.state(params)
        hv = self._hv(np.real(v)) + 1j * self._hv(np.imag(v))
        return float(np.real(v.conj() @ hv))

    def surrogate_loss(self, params, budget):
        terms = dict(self.terms)
        for g in reversed(self.gates):
            if g[0] == "cz":
                i, j = g[1], g[2]
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
                    keep = sorted(new, key=lambda kk: -abs(new[kk]))[:budget]
                    new = {kk: new[kk] for kk in keep}
                terms = new
        return float(sum(c for (x, z), c in terms.items() if x == 0))


def _setp(x, z, q, a):
    x &= ~(1 << q)
    z &= ~(1 << q)
    if a in (1, 3):
        x |= 1 << q
    if a in (2, 3):
        z |= 1 << q
    return x, z


LADDER = (32, 128, 512, 2048, 8192, 32768, 131072)


def budget_needed(inst, params, tol):
    ex = inst.exact_loss(params)
    for Nb in LADDER:
        if abs(inst.surrogate_loss(params, Nb) - ex) <= tol:
            return Nb
    return None


def scan(ns=(6, 7, 8, 9, 10, 11, 12), eps=0.1, steps=100, lr=0.05,
         h=1e-4, marks=(0.5, 0.9, 0.95)):
    rows = []
    for n in ns:
        inst = Inst(n)
        rng = np.random.default_rng(500 + n)
        th = eps * rng.normal(size=inst.nparam)
        L0 = inst.exact_loss(th)
        gap0 = L0 - inst.emin
        hit = {p: None for p in marks}
        for t in range(steps + 1):
            lo = inst.exact_loss(th)
            prog = (L0 - lo) / gap0
            for p in marks:
                if hit[p] is None and prog >= p:
                    hit[p] = (t, th.copy(), lo)
            if all(v is not None for v in hit.values()):
                break
            g = np.zeros(inst.nparam)
            for k in range(inst.nparam):
                p1, p2 = th.copy(), th.copy()
                p1[k] += h
                p2[k] -= h
                g[k] = (inst.exact_loss(p1) - inst.exact_loss(p2)) / (2 * h)
            th = th - lr * g
        tol = 0.0125 * n
        for p in marks:
            if hit[p] is None:
                print(f"  n={n} p={p}: NOT REACHED in {steps} steps")
                continue
            t, thp, lo = hit[p]
            gn = float(np.linalg.norm(_grad(inst, thp, h)))
            nb = budget_needed(inst, thp, tol)
            rows.append(dict(n=n, progress=p, step=t, loss=lo,
                             grad=gn, nstar=nb))
            print(f"  n={n:>2} p={p:.2f} t={t:>3} loss={lo:>9.4f} "
                  f"|grad|={gn:>7.3f}  N*={nb}", flush=True)
    return rows


def _grad(inst, th, h):
    g = np.zeros(inst.nparam)
    for k in range(inst.nparam):
        p1, p2 = th.copy(), th.copy()
        p1[k] += h
        p2[k] -= h
        g[k] = (inst.exact_loss(p1) - inst.exact_loss(p2)) / (2 * h)
    return g


def fits(rows, p=0.9):
    pts = [(r["n"], r["nstar"]) for r in rows
           if r["progress"] == p and r["nstar"]]
    if len(pts) < 4:
        return None
    x = np.array([q[0] for q in pts], float)
    y = np.log2([q[1] for q in pts])

    def fit(xs):
        A = np.vstack([xs, np.ones_like(xs)]).T
        sol, res, *_ = np.linalg.lstsq(A, y, rcond=None)
        ss = ((y - y.mean()) ** 2).sum()
        r2 = 1 - float(res[0]) / ss if len(res) and ss > 0 else 1.0
        return float(sol[0]), r2

    a_exp, r2_exp = fit(x)             # log2 N* ~ alpha * n
    a_pol, r2_pol = fit(np.log2(x))    # log2 N* ~ k * log2 n
    return dict(alpha=a_exp, r2_exp=r2_exp, degree=a_pol, r2_pol=r2_pol)


if __name__ == "__main__":
    print("K3 scan: budget at matched progress, n = 6..12, eps = 0.1\n")
    rows = scan()
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"\nappended {len(rows)} rows to {CSV.name}")
    for p in (0.5, 0.9, 0.95):
        f = fits(rows, p)
        if f:
            print(f"p={p}: exp fit alpha={f['alpha']:+.2f} bits/qubit "
                  f"(R2 {f['r2_exp']:.2f}); poly fit degree="
                  f"{f['degree']:+.1f} (R2 {f['r2_pol']:.2f})")
    print("\nPre-registered: K3 fires if poly fit >= exp fit and "
          "alpha < 0.5;\nsurvives if alpha >= 1.0 (R2>0.9) with "
          "non-collapsing gradients.")
