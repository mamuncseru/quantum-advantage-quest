"""T1/K4: the decisive scaling scan — does the trainable signal escape
the poly surrogate, or is it exactly the surrogatable part?

Protocol (fixed by the T1 brief before this file ran at scale): TFIM-DLA
sandwich V2(phi) . U_box . V1(theta) on input |0^n>, O = Z_1, box =
depth-ceil(c log2 n) NONLOCAL random 2-qubit gates, c in {1, 2}. The
poly adversary learns the module block T of Ad_U (the n(2n-1)-dim
quadratic sector) and tracks the block loss; the RESIDUAL
loss_res = loss - loss_block is what it cannot see.

Measured vs n (n = 4..nmax, exact statevector):
  Var_theta[d loss_tot],  Var_theta[d loss_block],
  Var_theta[d loss_res],  module mass of U^dag O U,  |loss| scale.
Control: a deep box (depth 2n) calibrates what exponential collapse
looks like at these sizes.

PRE-REGISTERED VERDICT (written before running at scale):
  - K4 FIRES (dichotomy wins, T1 closes as boundary theorem) if the
    residual-gradient variance decays at >= 0.5 bits/qubit with
    R^2 > 0.9 over n = 5..nmax while total gradients decay strictly
    slower — the trainable signal is the surrogatable part.
  - T1 SURVIVES if the residual rate is <= 0.2 bits/qubit — escalate
    to an L10-style lower-bound attempt.
  - Anything else: inconclusive; extend n or bring theory.

Run: .venv/bin/python hunt/code/t1_k4_scan.py [--nmax 9]
CSV appended to hunt/t1-k4-scan.csv (repo convention).
"""

import argparse
import csv
import sys
from math import ceil, log2
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).parent))

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "t1-k4-scan.csv"


# ------------------------------ Majorana ops as signed permutations ----

def majorana_perm(n, idx):
    """c_idx as (perm, coef): Op|b> = coef[b] |perm[b]>."""
    site, kind = divmod(idx, 2)
    dim = 2 ** n
    b = np.arange(dim)
    bits = (b[:, None] >> (n - 1 - np.arange(n))) & 1
    tail = (-1.0) ** bits[:, :site].sum(1)
    flip = b ^ (1 << (n - 1 - site))
    if kind == 0:                                    # Z-tail X
        coef = tail.astype(complex)
    else:                                            # Z-tail Y
        coef = tail * 1j * (-1.0) ** bits[:, site]
    return flip, coef


def compose(p1, c1, p2, c2):
    """(Op2 Op1)|b> = c1[b] c2[p1[b]] |p2[p1[b]]>."""
    return p2[p1], c1 * c2[p1]


def quad_basis(n):
    """Hermitian module basis i c_a c_b (a < b) as signed permutations."""
    cs = [majorana_perm(n, a) for a in range(2 * n)]
    out = []
    for a in range(2 * n):
        for b in range(a + 1, 2 * n):
            p, c = compose(*cs[a], *cs[b])          # c_b after c_a? order:
            # compose(p1,c1,p2,c2) = Op2 Op1; we want c_a c_b = Op(a) Op(b)
            p, c = compose(*cs[b], *cs[a])
            out.append((p, 1j * c))
    return out


def op_apply_left(pc, M):
    """B @ M for signed-permutation B."""
    p, c = pc
    out = np.empty_like(M)
    out[p, :] = c[:, None] * M
    return out


def op_trace_with(pc, M):
    """Tr(B M)."""
    p, c = pc
    return complex((c * M[np.arange(M.shape[0]), p][...]).sum()) \
        if False else complex(np.dot(c, M[np.arange(len(p)), p]))


def op_moment0(pc):
    """<0|B|0>."""
    p, c = pc
    return complex(c[0]) if p[0] == 0 else 0.0


# ------------------------------------------------------ per-n context ----

class Ctx:
    def __init__(self, n, layers=4):
        self.n, self.dim, self.layers = n, 2 ** n, 2 ** n and 2 ** n
        self.layers = layers
        dim = self.dim
        Xp = np.array([[0, 1], [1, 0]], dtype=complex)
        Zd = np.array([1.0, -1.0])

        def kron_all(mats):
            out = np.array([[1]], dtype=complex)
            for m in mats:
                out = np.kron(out, m)
            return out

        I2 = np.eye(2, dtype=complex)
        self.HXX = sum(
            kron_all([Xp if j in (i, i + 1) else I2 for j in range(n)])
            for i in range(n - 1))
        zdiag = np.zeros(dim)
        for i in range(n):
            zdiag += np.kron(np.kron(np.ones(2 ** i), Zd),
                             np.ones(2 ** (n - i - 1)))
        self.hz_diag = zdiag                        # HZ is diagonal
        w, V = np.linalg.eigh(self.HXX)
        self.xx_w, self.xx_V = w, V

        self.B = quad_basis(n)                      # module, dim n(2n-1)
        self.mod = len(self.B)
        HZ = np.diag(zdiag).astype(complex)
        self.AXX = self.ad_matrix(self.HXX)
        self.AZ = self.ad_matrix(HZ)
        self.o = np.array([np.real(op_trace_with(pc, self.zsite0()) / dim)
                           for pc in self.B])
        self.m = np.array([np.real(op_moment0(pc)) for pc in self.B])

    def zsite0(self):
        d = np.kron(np.array([1.0, -1.0]), np.ones(self.dim // 2))
        return np.diag(d).astype(complex)

    def ad_matrix(self, H):
        A = np.zeros((self.mod, self.mod))
        dim = self.dim
        for k, pc in enumerate(self.B):
            p, c = pc
            Bd = np.zeros((dim, dim), dtype=complex)
            Bd[p, np.arange(dim)] = c
            C = 1j * (H @ Bd - Bd @ H)
            for j, pcj in enumerate(self.B):
                A[j, k] = np.real(op_trace_with(pcj, C) / dim)
        return A

    # ---------------- state-vector ansatz application (fast) ----------
    def apply_ansatz(self, params, v):
        for l in range(self.layers):
            a, b = params[2 * l], params[2 * l + 1]
            v = self.xx_V @ (np.exp(-1j * a * self.xx_w) *
                             (self.xx_V.conj().T @ v))
            v = np.exp(-1j * b * self.hz_diag) * v
        return v

    def heis(self, coeff, params):
        for l in reversed(range(self.layers)):
            coeff = expm(params[2 * l + 1] * self.AZ) @ coeff
            coeff = expm(params[2 * l] * self.AXX) @ coeff
        return coeff


# ------------------------------------------------------------- box ----

def apply_gate(U, q, i, j, n):
    """(gate on qubits i,j) @ U for dense U."""
    dim = 2 ** n
    T = U.reshape((2,) * n + (dim,))
    T = np.tensordot(q.reshape(2, 2, 2, 2), T, axes=([2, 3], [i, j]))
    T = np.moveaxis(T, [0, 1], [i, j])
    return T.reshape(dim, dim)


def box(n, depth, rng):
    U = np.eye(2 ** n, dtype=complex)
    for _ in range(depth):
        order = rng.permutation(n)
        for k in range(n // 2):
            i, j = sorted((order[2 * k], order[2 * k + 1]))
            g = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
            q, _ = np.linalg.qr(g)
            U = apply_gate(U, q, i, j, n)
    return U


def module_block(ctx, U):
    """T[k,j] = Tr(B_k U^dag B_j U)/2^n and module mass of U^dag O U."""
    dim, mod = ctx.dim, ctx.mod
    flatPT = np.empty((mod, dim * dim), dtype=np.complex64)
    for j, pc in enumerate(ctx.B):
        flatPT[j] = op_apply_left(pc, U).T.ravel()
    T = np.empty((mod, mod))
    Ud = U.conj().T
    for k, pc in enumerate(ctx.B):
        Qk = op_apply_left(pc, Ud).ravel().astype(np.complex64)
        T[k] = np.real(flatPT @ Qk) / dim
    OU = Ud @ ctx.zsite0() @ U
    coeffs = np.array([op_trace_with(pc, OU) / dim for pc in ctx.B])
    return T, float(np.sum(np.abs(coeffs) ** 2))


# ------------------------------------------------------------- scan ----

def config_stats(ctx, U, T, samples, rng, h=1e-4):
    dim = ctx.dim
    psi0 = np.zeros(dim, dtype=complex)
    psi0[0] = 1.0
    gt, gb, gr, scale = [], [], [], []

    def total(th, ph):
        v = ctx.apply_ansatz(th, psi0)
        v = U @ v
        v = ctx.apply_ansatz(ph, v)
        d = np.kron(np.array([1.0, -1.0]), np.ones(dim // 2))
        return float(np.real(v.conj() @ (d * v)))

    def block(th, ph):
        coeff = ctx.heis(ctx.o, ph)
        coeff = T @ coeff
        coeff = ctx.heis(coeff, th)
        return float(coeff @ ctx.m)

    for _ in range(samples):
        th = rng.uniform(-np.pi, np.pi, 2 * ctx.layers)
        ph = rng.uniform(-np.pi, np.pi, 2 * ctx.layers)
        scale.append(abs(total(th, ph)))
        t1p, t1m = th.copy(), th.copy()
        t1p[0] += h
        t1m[0] -= h
        dtot = (total(t1p, ph) - total(t1m, ph)) / (2 * h)
        dblk = (block(t1p, ph) - block(t1m, ph)) / (2 * h)
        gt.append(dtot)
        gb.append(dblk)
        gr.append(dtot - dblk)
    return (float(np.var(gt)), float(np.var(gb)), float(np.var(gr)),
            float(np.mean(scale)))


def run(nmax, samples=36, seeds=(0, 1)):
    rows = []
    for n in range(4, nmax + 1):
        ctx = Ctx(n)
        for c in (1, 2, "deep"):
            d = 2 * n if c == "deep" else max(1, ceil(c * log2(n)))
            vt = vb = vr = m2 = sc = 0.0
            use = seeds if c != "deep" else seeds[:1]
            for s in use:
                rng = np.random.default_rng(9000 + 97 * n + 13 * d + s)
                U = box(n, d, rng)
                T, mass2 = module_block(ctx, U)
                a, b_, r, s_ = config_stats(ctx, U, T, samples, rng)
                vt += a / len(use)
                vb += b_ / len(use)
                vr += r / len(use)
                m2 += mass2 / len(use)
                sc += s_ / len(use)
            row = dict(n=n, c=str(c), depth=d, mass2=m2, var_tot=vt,
                       var_block=vb, var_res=vr, loss_scale=sc)
            rows.append(row)
            print(f"  n={n} c={c:>4} d={d:>2}  mass2={m2:.3f}  "
                  f"Var tot/blk/res = {vt:.3e} {vb:.3e} {vr:.3e}  "
                  f"|loss|={sc:.3f}")
    return rows


def fit_rate(rows, key, c, nmin=5):
    pts = [(r["n"], r[key]) for r in rows
           if r["c"] == str(c) and r["n"] >= nmin and r[key] > 0]
    if len(pts) < 3:
        return None, None
    x = np.array([p[0] for p in pts], float)
    y = np.log2([p[1] for p in pts])
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, _), res, *_ = np.linalg.lstsq(A, y, rcond=None)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float(res[0]) / ss_tot if len(res) and ss_tot > 0 else 1.0
    return -float(slope), r2          # decay rate in bits/qubit


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=9)
    ap.add_argument("--samples", type=int, default=36)
    args = ap.parse_args()

    print(f"K4 scan: n = 4..{args.nmax}, nonlocal boxes at depth "
          f"ceil(c log2 n), c in {{1,2}}, control depth 2n\n")
    rows = run(args.nmax, samples=args.samples)

    new = not CSV.exists()
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"\nappended {len(rows)} rows to {CSV.name}")

    print("\ndecay rates (bits/qubit, fit n>=5):")
    print(f"  {'c':>5} {'total':>14} {'block':>14} {'residual':>14}")
    for c in (1, 2, "deep"):
        cells = []
        for key in ("var_tot", "var_block", "var_res"):
            rate, r2 = fit_rate(rows, key, c)
            cells.append(f"{rate:+.2f} (R2 {r2:.2f})" if rate is not None
                         else "—")
        print(f"  {str(c):>5} {cells[0]:>14} {cells[1]:>14} {cells[2]:>14}")
    print("\nPre-registered thresholds: K4 fires if residual >= 0.5 "
          "bits/qubit (R2>0.9)\nand total strictly slower; survives if "
          "residual <= 0.2; else inconclusive.")
