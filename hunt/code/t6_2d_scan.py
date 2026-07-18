"""T6 continuation: the 2D control window — does the MPO attack that
killed the 1D instance fail on a 4x4 lattice?

K4-t6 closed T6's 1D form: bond-32 MPOs track 1D heating trajectories.
The pre-registered surviving form is >=2D, where the snake-ordered MPO
must carry vertical bonds as long-range couplings and bond dimension
fights the cut. Same protocol as 1D for comparability: H = sum_<ij>
Z_i Z_j + g sum X_i on a 4x4 open lattice (g = 3.0, near the 2D
quantum-critical point), checkerboard staggered-Z drive, K = 6
segments x 3 Trotter steps of dt = 0.1 (T = 1.8), gradient ASCENT of
<H> from the ground state, 30 steps.

Measured at trajectory checkpoints: exact <H>, gradient norm, Pauli
budget N* (ladder to 8192), and MPO error at chi in {16, 32, 64, 128}
(tolerance 0.0125 n = 0.2).

PRE-REGISTERED (before running at scale):
  - T6-2D HARDENS if chi*(t=30) >= 128 (>= 4x the 1D answer) — bond
    growth with dimensionality as the hardness consensus predicts;
    formal survival then still owes the size scan (4x5, 4x6).
  - The MPO attack LANDS AGAIN (T6 closes outright at reachable sizes)
    if chi*(t=30) <= 32 in 2D as well.
  - Machinery gate: the 2x3 lattice (n = 6, chi = 64 exact) must
    reproduce dense conjugation to machine precision first.

Run: .venv/bin/python hunt/code/t6_2d_scan.py    (hours; background)
"""

import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).parent))
from t4_adaptive_growth import anticommute, pmult  # noqa: E402
from t6_mpo_attack import (I2, X, Z, apply_single, compress,  # noqa: E402
                           mpo_add, mpo_apply, mult_in, mult_out)

HERE = Path(__file__).resolve().parent


# ------------------------------------------------- 2D lattice problem ----

def build2d(rows, cols, g=3.0, K=6, M=3, dt=0.1):
    n = rows * cols

    def site(r, c):
        # snake ordering: even rows left-to-right, odd rows reversed
        return r * cols + (c if r % 2 == 0 else cols - 1 - c)

    bonds = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                bonds.append(tuple(sorted((site(r, c), site(r, c + 1)))))
            if r + 1 < rows:
                bonds.append(tuple(sorted((site(r, c), site(r + 1, c)))))
    stag = np.empty(n)
    for r in range(rows):
        for c in range(cols):
            stag[site(r, c)] = (-1.0) ** (r + c)
    return dict(n=n, rows=rows, cols=cols, g=g, K=K, M=M, dt=dt,
                bonds=bonds, stag=stag)


def gate_seq(P, theta):
    g = []
    for j in range(P["K"]):
        for _ in range(P["M"]):
            for (a, b) in P["bonds"]:
                g.append(("zz", (a, b), P["dt"]))
            for i in range(P["n"]):
                g.append(("z", (i,), P["dt"] * theta[j] * P["stag"][i]))
            for i in range(P["n"]):
                g.append(("x", (i,), P["dt"] * P["g"]))
    return g


# ------------------------------------------------- statevector arm ----

class SV:
    def __init__(self, P):
        self.P = P
        n = P["n"]
        self.dim = 2 ** n
        b = np.arange(self.dim)
        diag = np.zeros(self.dim)
        for (i, j) in P["bonds"]:
            m = (1 << i) | (1 << j)
            odd = np.bitwise_count(b & m).astype(np.int64) & 1
            diag += 1.0 - 2.0 * odd
        self.diag_zz = diag
        sd = np.zeros(self.dim)
        for i in range(n):
            odd = np.bitwise_count(b & (1 << i)).astype(np.int64) & 1
            sd += P["stag"][i] * (1.0 - 2.0 * odd)
        self.stag_diag = sd
        op = LinearOperator((self.dim, self.dim),
                            matvec=lambda v: self.hv(v.astype(complex)),
                            dtype=complex)
        w, v = eigsh(op, k=1, which="SA")
        self.emin, self.psi0 = float(np.real(w[0])), v[:, 0].astype(complex)
        self.emax = float(np.real(
            eigsh(op, k=1, which="LA")[0][0]))

    def hv(self, v):
        out = self.diag_zz * v
        b = np.arange(self.dim)
        for i in range(self.P["n"]):
            out = out + self.P["g"] * v[b ^ (1 << i)]
        return out

    def evolve(self, theta):
        P, n = self.P, self.P["n"]
        v = self.psi0.copy()
        for j in range(P["K"]):
            dphase = np.exp(-1j * P["dt"] * (self.diag_zz
                                             + theta[j] * self.stag_diag))
            for _ in range(P["M"]):
                v = dphase * v
                a = P["dt"] * P["g"]
                for q in range(n):
                    v = v.reshape(2 ** (n - 1 - q), 2, 2 ** q)
                    v0, v1 = v[:, 0].copy(), v[:, 1].copy()
                    v[:, 0] = np.cos(a) * v0 - 1j * np.sin(a) * v1
                    v[:, 1] = np.cos(a) * v1 - 1j * np.sin(a) * v0
                    v = v.reshape(-1)
        return v

    def loss(self, theta):
        v = self.evolve(theta)
        return float(np.real(v.conj() @ self.hv(v)))

    def grad(self, theta, h=1e-4):
        g = np.zeros(len(theta))
        for k in range(len(theta)):
            p1, p2 = theta.copy(), theta.copy()
            p1[k] += h
            p2[k] -= h
            g[k] = (self.loss(p1) - self.loss(p2)) / (2 * h)
        return g


# ------------------------------------------------- Pauli-budget arm ----

def pauli_surrogate(sv, theta, budget):
    P = sv.P
    terms = {}
    for (i, j) in P["bonds"]:
        terms[(0, (1 << i) | (1 << j))] = 1.0
    for i in range(P["n"]):
        terms[((1 << i), 0)] = P["g"]
    for (kind, sites, th) in reversed(gate_seq(P, theta)):
        if kind == "zz":
            gx, gz = 0, (1 << sites[0]) | (1 << sites[1])
        elif kind == "z":
            gx, gz = 0, (1 << sites[0])
        else:
            gx, gz = (1 << sites[0]), 0
        co, si = np.cos(2 * th), np.sin(2 * th)
        new = {}
        for (x, z), c in terms.items():
            if not anticommute(gx, gz, x, z):
                new[(x, z)] = new.get((x, z), 0.0) + c
            else:
                new[(x, z)] = new.get((x, z), 0.0) + co * c
                x3, z3, ph = pmult(gx, gz, x, z)
                w = 1j * ph
                new[(x3, z3)] = new.get((x3, z3), 0.0) + si * w.real * c
        if budget and len(new) > budget:
            keep = sorted(new, key=lambda kk: -abs(new[kk]))[:budget]
            new = {kk: new[kk] for kk in keep}
        terms = new
    b = np.arange(sv.dim)
    val = 0.0
    for (x, z), c in terms.items():
        ny = int(x & z).bit_count()
        ph = (1j) ** ny * (1 - 2 * (np.bitwise_count(b & z)
                                    .astype(np.int64) & 1))
        w = np.empty_like(sv.psi0)
        w[b ^ x] = ph * sv.psi0
        val += c * float(np.real(sv.psi0.conj() @ w))
    return val


def pauli_budget(sv, theta, tol, ladder=(128, 512, 2048, 8192)):
    ex = sv.loss(theta)
    for Nb in ladder:
        if abs(pauli_surrogate(sv, theta, Nb) - ex) <= tol:
            return Nb
    return None


# ------------------------------------------------------- MPO arm ----

def term_mpo(n, ops):
    """Bond-1 MPO for a product of single-site ops {site: 2x2 matrix}."""
    Ws = []
    for i in range(n):
        W = np.zeros((1, 2, 2, 1), dtype=complex)
        W[0, :, :, 0] = ops.get(i, I2)
        Ws.append(W)
    return Ws


def h_mpo_2d(P):
    """Exact H MPO by term-summing + lossless compression."""
    n = P["n"]
    parts = [term_mpo(n, {i: Z, j: Z}) for (i, j) in P["bonds"]]
    for i in range(n):
        t = term_mpo(n, {i: X})
        t[0] = t[0] * P["g"]
        parts.append(t)
    Ws = parts[0]
    for t in parts[1:]:
        Ws = mpo_add(Ws, t)
    return compress(Ws, chi=4096)          # lossless (tol-based rank cut)


def mpo_conjugate_2d(P, theta, chi):
    Ws = h_mpo_2d(P)
    for (kind, sites, th) in reversed(gate_seq(P, theta)):
        c1, s1 = np.cos(th), np.sin(th)
        if kind in ("z", "x"):
            m = Z if kind == "z" else X
            apply_single(Ws, c1 * I2 - 1j * s1 * m, sites[0])
            continue
        q1, q2 = sites
        A = [W.copy() for W in Ws]
        Bm = [W.copy() for W in Ws]
        mult_out(Bm, Z, q1)
        mult_out(Bm, Z, q2)
        mult_in(Bm, Z, q1)
        mult_in(Bm, Z, q2)
        Cm = [W.copy() for W in Ws]
        mult_out(Cm, Z, q1)
        mult_out(Cm, Z, q2)
        Dm = [W.copy() for W in Ws]
        mult_in(Dm, Z, q1)
        mult_in(Dm, Z, q2)
        A[0] = A[0] * (c1 * c1)
        Bm[0] = Bm[0] * (s1 * s1)
        Cm[0] = Cm[0] * (1j * c1 * s1)
        Dm[0] = Dm[0] * (-1j * c1 * s1)
        Ws = compress(mpo_add(A, Bm, Cm, Dm), chi)
    return Ws


def mpo_loss_2d(sv, theta, chi):
    Ws = mpo_conjugate_2d(sv.P, theta, chi)
    return float(np.real(sv.psi0.conj() @ mpo_apply(Ws, sv.psi0)))


# ------------------------------------------------------------ main ----

if __name__ == "__main__":
    # machinery gate: 2x3 lattice, chi = 64 exact
    from t6_mpo_attack import dense_evolved  # noqa: F401
    P6 = build2d(2, 3, K=2, M=2)
    sv6 = SV(P6)
    rng = np.random.default_rng(3)
    th6 = rng.uniform(-0.8, 0.8, P6["K"])
    v_mpo = mpo_loss_2d(sv6, th6, 64)
    v_ex = sv6.loss(th6)
    v_pp = pauli_surrogate(sv6, th6, None)
    print("machinery gate (2x3, chi=64 exact):")
    print(f"  MPO vs exact:   {abs(v_mpo - v_ex):.2e}")
    print(f"  Pauli vs exact: {abs(v_pp - v_ex):.2e}\n", flush=True)
    assert abs(v_mpo - v_ex) < 1e-8 and abs(v_pp - v_ex) < 1e-8

    # 4x4 heating trajectory
    P = build2d(4, 4)
    sv = SV(P)
    tol = 0.0125 * P["n"]
    print(f"4x4: E_min = {sv.emin:.4f}, E_max = {sv.emax:.4f}, "
          f"tol = {tol}", flush=True)
    th = 0.1 * np.random.default_rng(20260718).normal(size=P["K"])
    marks = {}
    for t in range(31):
        if t in (0, 10, 30):
            marks[t] = th.copy()
        if t < 30:
            th = th + 0.2 * sv.grad(th)
    for t, thc in sorted(marks.items()):
        ex = sv.loss(thc)
        gn = float(np.linalg.norm(sv.grad(thc)))
        nb = pauli_budget(sv, thc, tol)
        print(f"t={t:>2} <H>={ex:>9.4f} (frac of E_max "
              f"{(ex - sv.emin) / (sv.emax - sv.emin):.2f}) "
              f"|grad|={gn:.3f} N*={nb}", flush=True)
        for chi in (16, 32, 64, 128):
            err = abs(mpo_loss_2d(sv, thc, chi) - ex)
            print(f"      chi={chi:>4}: MPO err = {err:.4f}", flush=True)
    print("\nPre-registered: hardens if chi*(t=30) >= 128; MPO lands "
          "again if chi*(t=30) <= 32.")
