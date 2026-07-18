"""K4-t6: the MPO attack on T6's survivor — can a tensor-network
surrogate track the heating trajectory that defeated Pauli truncation?

The attack: Heisenberg-evolve the objective through the control circuit
as a Matrix Product Operator with bond dimension chi, truncating by SVD
after every entangling gate; evaluate on the known start state. The
final-time operator entanglement measured in T6 (~2.9 bits, effective
rank ~8) suggests chi ~ 8-32 might suffice at n = 10 — but the MPO must
survive every INTERMEDIATE step, and operator-entanglement barriers
mid-evolution are exactly what the S_op-at-final-time proxy cannot see.

  K4a (evaluation): chi*(t) = minimal bond with |MPO loss - exact| <=
      0.1 along the exact-driven heating trajectory's checkpoints.
      If chi* stays ~8-32, the attack lands (T6's n=10 evidence is
      Pauli-truncation-specific); if intermediate barriers force chi*
      up the ladder, the attack fails and the survivor hardens.
  K4b (operational, if K4a lands): MPO-driven ascent vs exact-driven.

Machinery is hand-built (numpy only, house rules) and validated the
house way: at n = 6, chi = 64 is EXACT (4^3 at the middle cut), so the
full MPO pipeline must reproduce dense conjugation to machine
precision before any attack number is believed.

Run: .venv/bin/python hunt/code/t6_mpo_attack.py    (~30 min)
"""

import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).parent))

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


# ------------------------------------------------- problem definition ----

def build(n, K=6, M=3, dt=0.1):
    """Same physics as t6_control_window, parameterized by n."""
    terms = {}
    for i in range(n - 1):
        terms[("zz", i)] = 1.0
    for i in range(n):
        terms[("x", i)] = 1.0
    for i in range(n - 2):
        terms[("zz2", i)] = 0.4
    stag = [(-1.0) ** i for i in range(n)]
    return dict(n=n, K=K, M=M, dt=dt, terms=terms, stag=stag)


def gate_seq(P, theta):
    """(kind, sites, angle) in the order evolve applies them."""
    g = []
    for j in range(P["K"]):
        for _ in range(P["M"]):
            for (kind, i), c in P["terms"].items():
                if kind == "zz":
                    g.append(("zz", (i, i + 1), P["dt"] * c))
                elif kind == "zz2":
                    g.append(("zz", (i, i + 2), P["dt"] * c))
            for i, s in enumerate(P["stag"]):
                g.append(("z", (i,), P["dt"] * theta[j] * s))
            for (kind, i), c in P["terms"].items():
                if kind == "x":
                    g.append(("x", (i,), P["dt"] * c))
    return g


# --------------------------------------------- dense reference (small) ----

def site_op(op, i, n):
    M_ = np.array([[1]], dtype=complex)
    for q in range(n):
        M_ = np.kron(M_, op if q == i else I2)
    return M_


def dense_H(P):
    n = P["n"]
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for (kind, i), c in P["terms"].items():
        if kind == "zz":
            H += c * site_op(Z, i, n) @ site_op(Z, i + 1, n)
        elif kind == "zz2":
            H += c * site_op(Z, i, n) @ site_op(Z, i + 2, n)
        else:
            H += c * site_op(X, i, n)
    return H


def dense_evolved(P, theta, O):
    n = P["n"]
    for (kind, sites, th) in reversed(gate_seq(P, theta)):
        if kind == "zz":
            Pm = site_op(Z, sites[0], n) @ site_op(Z, sites[1], n)
        elif kind == "z":
            Pm = site_op(Z, sites[0], n)
        else:
            Pm = site_op(X, sites[0], n)
        c1, s1 = np.cos(th), np.sin(th)
        O = c1 * c1 * O + s1 * s1 * (Pm @ O @ Pm) \
            + 1j * c1 * s1 * (Pm @ O - O @ Pm)
    return O


# ----------------------------------------------------- MPO machinery ----

def h_mpo(P):
    """Exact MPO of H (bond 5): FSA channels
    0 pass-before, 1 Z-awaiting-nn, 2 Z-awaiting-nnn, 3 skip, 4 done."""
    n = P["n"]
    Ws = []
    for i in range(n):
        W = np.zeros((5, 2, 2, 5), dtype=complex)
        W[0, :, :, 0] = I2
        W[4, :, :, 4] = I2
        W[0, :, :, 4] = X * 1.0                     # field term
        if i < n - 1:
            W[0, :, :, 1] = Z                       # start nn ZZ
        W[1, :, :, 4] = Z                           # complete nn (any i)
        if i < n - 2:
            W[0, :, :, 2] = Z * 0.4                 # start nnn ZZ'
        W[2, :, :, 3] = I2
        W[3, :, :, 4] = Z
        Ws.append(W)
    Ws[0] = Ws[0][:1]                               # boundary row 0
    Ws[-1] = Ws[-1][:, :, :, 4:5]                   # boundary col 4
    return Ws


def mpo_to_dense(Ws):
    n = len(Ws)
    T = Ws[0]
    for i in range(1, n):
        T = np.einsum('a...b,bstc->a...stc', T, Ws[i])
    T = T[0, ..., 0]
    # legs: s1 s1' s2 s2' ... -> (s1..sn),(s1'..sn')
    order = list(range(0, 2 * n, 2)) + list(range(1, 2 * n, 2))
    return T.transpose(order).reshape(2 ** n, 2 ** n)


def apply_single(Ws, u, q):
    Ws[q] = np.einsum('st,atub,uv->asvb', u.conj().T, Ws[q], u)


def mult_out(Ws, m, q):
    """O <- m O (left-multiply site q's out leg)."""
    Ws[q] = np.einsum('st,atub->asub', m, Ws[q])


def mult_in(Ws, m, q):
    """O <- O m (right-multiply site q's in leg)."""
    Ws[q] = np.einsum('atub,uv->atvb', Ws[q], m)


def mpo_add(As, Bs, *more):
    """Direct-sum bond stacking of MPOs."""
    all_ = [As, Bs, *more]
    n = len(As)
    out = []
    for i in range(n):
        blocks = [W[i] for W in all_]
        if i == 0:
            out.append(np.concatenate(blocks, axis=3))
        elif i == n - 1:
            out.append(np.concatenate(blocks, axis=0))
        else:
            dl = sum(b.shape[0] for b in blocks)
            dr = sum(b.shape[3] for b in blocks)
            W = np.zeros((dl, 2, 2, dr), dtype=complex)
            l = r = 0
            for b in blocks:
                W[l:l + b.shape[0], :, :, r:r + b.shape[3]] = b
                l += b.shape[0]
                r += b.shape[3]
            out.append(W)
    return out


def compress(Ws, chi):
    """Two-pass canonical compression to bond <= chi."""
    n = len(Ws)
    # left-to-right QR
    for i in range(n - 1):
        a, s, t, b = Ws[i].shape
        Mt = Ws[i].reshape(a * 4, b)
        Q, R = np.linalg.qr(Mt)
        Ws[i] = Q.reshape(a, s, t, Q.shape[1])
        Ws[i + 1] = np.einsum('ab,bstc->astc', R, Ws[i + 1])
    # right-to-left SVD with truncation
    for i in range(n - 1, 0, -1):
        a, s, t, b = Ws[i].shape
        Mt = Ws[i].reshape(a, 4 * b)
        U, S, Vh = np.linalg.svd(Mt, full_matrices=False)
        k = min(chi, int((S > 1e-13).sum()) or 1)
        Ws[i] = (Vh[:k]).reshape(k, s, t, b)
        Ws[i - 1] = np.einsum('astb,bc->astc', Ws[i - 1],
                              (U[:, :k] * S[:k]))
    return Ws


def mpo_conjugate(P, theta, chi):
    """Heisenberg-evolve H through the circuit as a chi-MPO."""
    Ws = h_mpo(P)
    for (kind, sites, th) in reversed(gate_seq(P, theta)):
        c1, s1 = np.cos(th), np.sin(th)
        if kind in ("z", "x"):
            m = Z if kind == "z" else X
            u = c1 * I2 - 1j * s1 * m               # e^{-i th m}
            apply_single(Ws, u, sites[0])
            continue
        q1, q2 = sites
        A = [W.copy() for W in Ws]                  # O
        Bm = [W.copy() for W in Ws]                 # P O P
        mult_out(Bm, Z, q1)
        mult_out(Bm, Z, q2)
        mult_in(Bm, Z, q1)
        mult_in(Bm, Z, q2)
        Cm = [W.copy() for W in Ws]                 # P O
        mult_out(Cm, Z, q1)
        mult_out(Cm, Z, q2)
        Dm = [W.copy() for W in Ws]                 # O P
        mult_in(Dm, Z, q1)
        mult_in(Dm, Z, q2)
        A[0] = A[0] * (c1 * c1)
        Bm[0] = Bm[0] * (s1 * s1)
        Cm[0] = Cm[0] * (1j * c1 * s1)
        Dm[0] = Dm[0] * (-1j * c1 * s1)
        Ws = compress(mpo_add(A, Bm, Cm, Dm), chi)
    return Ws


def mpo_apply(Ws, psi):
    """O|psi> for dense psi. Invariant: entering step i, R has legs
    (bond, s_1..s_{i-1}, t_i, t_{i+1}..t_n) — output bits accumulate on
    the left, unconsumed input bits sit from position i onward."""
    n = len(Ws)
    R = psi.reshape((2,) * n)[np.newaxis, ...]       # (a=1, t_1..t_n)
    for i in range(n):
        # entering step i (0-based): legs (bond, s_0..s_{i-1}, t_i..t_n),
        # so t_i sits at axis 1 + i
        R = np.tensordot(Ws[i], R, axes=([0, 2], [0, 1 + i]))
        # result legs: (s_i, b, s_0..s_{i-1}, t_{i+1}..t_n)
        R = np.moveaxis(R, 1, 0)                     # bond to front
        R = np.moveaxis(R, 1, 1 + i)                 # s_i after s_{i-1}
    return R[0].reshape(-1)


def mpo_loss(P, theta, chi, psi0):
    Ws = mpo_conjugate(P, theta, chi)
    return float(np.real(psi0.conj() @ mpo_apply(Ws, psi0)))


# ------------------------------------------------------------ ground ----

def ground_state(P):
    n = P["n"]
    H = dense_H(P)
    w, v = np.linalg.eigh(H)
    return v[:, 0].astype(complex), float(w[0])


if __name__ == "__main__":
    # stage 1: exactness at n=6 (chi=64 is exact there)
    P6 = build(6, K=2, M=2)
    rng = np.random.default_rng(3)
    th = rng.uniform(-0.8, 0.8, P6["K"])
    psi6, _ = ground_state(P6)
    Hd = dense_H(P6)
    ref = dense_evolved(P6, th, Hd.copy())
    val_ref = float(np.real(psi6.conj() @ (ref @ psi6)))
    print("stage 1 — n=6 validation (chi=64 exact):")
    print(f"  H-MPO vs dense H: "
          f"{np.abs(mpo_to_dense(h_mpo(P6)) - Hd).max():.2e}")
    v64 = mpo_loss(P6, th, 64, psi6)
    print(f"  full pipeline vs dense conjugation: {abs(v64-val_ref):.2e}")

    # stage 2 — K4a at n=10 along the exact heating trajectory
    import t6_control_window as t6
    P10 = build(10, K=6, M=3)
    psi10 = t6.PSI0.copy()
    obj = dict(t6.HTERMS)
    rng2 = np.random.default_rng(20260718)
    for name, o in t6.OBJ.items():
        for _ in range(8):
            rng2.uniform(-1.0, 1.0, t6.K)
    _ = 0.1 * rng2.normal(size=t6.K)
    th_t = 0.1 * rng2.normal(size=t6.K)
    traj = {0: th_t.copy()}
    for t in range(1, 31):
        g = np.zeros(t6.K)
        for k in range(t6.K):
            p1, p2 = th_t.copy(), th_t.copy()
            p1[k] += 1e-4
            p2[k] -= 1e-4
            g[k] = (t6.loss(p1, obj) - t6.loss(p2, obj)) / 2e-4
        th_t = th_t + 0.2 * g
        if t in (10, 30):
            traj[t] = th_t.copy()
    print("\nstage 2 — K4a: chi* along the exact heating trajectory (n=10)")
    print(f"  {'t':>3} {'exact <H>':>10}  chi ladder errors (4, 8, 16, 32, 64)")
    for t, th_c in sorted(traj.items()):
        ex = t6.loss(th_c, obj)
        errs = []
        for chi in (4, 8, 16, 32, 64):
            errs.append(abs(mpo_loss(P10, th_c, chi, psi10) - ex))
        e = "  ".join(f"{x:.3f}" for x in errs)
        print(f"  {t:>3} {ex:>10.4f}  [{e}]", flush=True)
