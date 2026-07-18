"""T6 first numerics: the control window — does optimizing physical
response objectives steer dynamics INTO the classically expensive
region, or do optimizers avoid scrambling here too?

Setting (the honest evaluation-hardness instance): quantum optimal
control. K = 6 trainable parameters (piecewise-constant staggered-field
drive) — few parameters, so barren plateaus cannot apply; loss = a
physical observable after Trotterized real-time evolution of a
nonintegrable chain — O(1) values, so the concentration trap (where
"output 0" passes additive-error evaluation) cannot apply; the
evaluation oracle is Hamiltonian dynamics, whose classical hardness
pedigree (BQP-completeness) is the strongest available. At scan sizes
everything is classically easy — as always, the instrument measures the
MECHANISM: do the classical-cost proxies grow along training?

Model: H = sum Z_i Z_{i+1} + g sum X_i + 0.4 sum Z_i Z_{i+2} (g = 1),
n = 10; drive H_c = sum (-1)^i Z_i; K = 6 segments, each 5 Trotter
steps of dt = 0.1 (the Trotter circuit IS the model — no Trotter-error
debate). Start state: ground state of H.

Objectives (gradient ASCENT, 30 steps):
  A (order):   maximize staggered magnetization <M_st> at final time.
  B (heating): maximize <H> at final time — the objective with a
               physical reason to reward scrambling.

Measured along each trajectory and on a 20-draw random-theta baseline:
  loss, |grad|, N* (Pauli-propagation budget for error <= 0.1, T4
  engine), and S_op (operator entanglement of the Heisenberg-evolved
  objective across the middle cut — the tensor-network cost proxy).

PRE-REGISTERED (before running at scale):
  K1 fires (sixth face) if, for BOTH objectives, trained-trajectory
  N* and S_op stay at or below the random-theta baseline (training
  avoids scrambling relative to generic controls).
  T6 SURVIVES if for some physical objective the proxies grow along
  training — above baseline and rising — while gradients stay O(1).
  K3 (operational, owed if survival): surrogate-driven ascent at
  fixed budget must FAIL to match the exact-driven final value.

Run: .venv/bin/python hunt/code/t6_control_window.py   (~10 min)
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).parent))
from t4_adaptive_growth import anticommute, pmult  # noqa: E402

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "t6-control-scan.csv"

N = 10
DIM = 2 ** N
K = 6                       # drive segments
M_TROT = 3                  # Trotter steps per segment
DT = 0.1
LADDER = (128, 512, 2048, 8192)   # None = beyond 8192: saturated


def zdiag(z_mask):
    b = np.arange(DIM)
    odd = np.bitwise_count(b & z_mask).astype(np.int64) & 1
    return 1.0 - 2.0 * odd


# Hamiltonian terms (x_mask, z_mask): coeff — all real Pauli strings
HTERMS = {}
for i in range(N - 1):
    HTERMS[(0, (1 << i) | (1 << (i + 1)))] = 1.0
for i in range(N):
    HTERMS[((1 << i), 0)] = 1.0
for i in range(N - 2):
    HTERMS[(0, (1 << i) | (1 << (i + 2)))] = 0.4

STAG = {(0, (1 << i)): ((-1.0) ** i) for i in range(N)}   # H_c terms
MST = {(0, (1 << i)): ((-1.0) ** i) / N for i in range(N)}

DIAG_ZZ = sum(c * zdiag(z) for (x, z), c in HTERMS.items() if x == 0)
STAG_DIAG = sum(c * zdiag(z) for (x, z), c in STAG.items())


def hv(v):
    out = DIAG_ZZ * v
    b = np.arange(DIM)
    for (x, z), c in HTERMS.items():
        if x:
            out = out + c * v[b ^ x]
    return out


_op = LinearOperator((DIM, DIM), matvec=lambda v: hv(v.astype(complex)),
                     dtype=complex)
_w, _v = eigsh(_op, k=1, which="SA")
EMIN, PSI0 = float(np.real(_w[0])), _v[:, 0].astype(complex)


# --------------------------------------------------------- circuit ----

DIAG_TERMS = [(x, z, c) for (x, z), c in HTERMS.items() if x == 0]
X_TERMS = [(x, z, c) for (x, z), c in HTERMS.items() if x != 0]


def gate_list(theta):
    """Trotter circuit as explicit Pauli rotations, in EXACTLY the order
    evolve() applies them: all diagonals (ZZ, ZZ', drive), then X's."""
    gates = []
    for j in range(K):
        for _ in range(M_TROT):
            for (x, z, c) in DIAG_TERMS:
                gates.append((x, z, DT * c))
            for (x, z), c in STAG.items():          # drive segment j
                gates.append((x, z, DT * theta[j] * c))
            for (x, z, c) in X_TERMS:
                gates.append((x, z, DT * c))
    return gates


def evolve(theta):
    """Statevector evolution (diagonals fused; X's as RX gates)."""
    v = PSI0.copy()
    for j in range(K):
        dphase = np.exp(-1j * DT * (DIAG_ZZ + theta[j] * STAG_DIAG))
        for _ in range(M_TROT):
            v = dphase * v
            for q in range(N):                       # e^{-i dt X_q}
                v = v.reshape(2 ** (N - 1 - q), 2, 2 ** q)
                a, b = v[:, 0].copy(), v[:, 1].copy()
                v[:, 0] = np.cos(DT) * a - 1j * np.sin(DT) * b
                v[:, 1] = np.cos(DT) * b - 1j * np.sin(DT) * a
                v = v.reshape(-1)
    return v


def expect(v, terms):
    val, b = 0.0, np.arange(DIM)
    for (x, z), c in terms.items():
        if x == 0:
            val += c * float(np.real(v.conj() @ (zdiag(z) * v)))
        else:
            val += c * float(np.real(v.conj() @ v[b ^ x]))
    return val


def loss(theta, obj):
    return expect(evolve(theta), obj)


def grad(theta, obj, h=1e-4):
    g = np.zeros(K)
    for k in range(K):
        p1, p2 = theta.copy(), theta.copy()
        p1[k] += h
        p2[k] -= h
        g[k] = (loss(p1, obj) - loss(p2, obj)) / (2 * h)
    return g


# ------------------------------------- classical-cost proxies ----------

def surrogate_loss(theta, obj, budget):
    """<psi0| C^dag O C |psi0> by truncated backward conjugation, then
    exact evaluation of the surviving terms on the known start state."""
    terms = dict(obj)
    for (gx, gz, th) in reversed(gate_list(theta)):
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
    # evaluation on the KNOWN start state (granted to the surrogate —
    # conservative: strengthens kills, is honest for survival claims,
    # since the question is the cost of the DYNAMICS)
    return sum(c * pauli_expect(PSI0, x, z) for (x, z), c in terms.items())


def pauli_expect(v, x, z):
    b = np.arange(DIM)
    ny = int(x & z).bit_count()
    ph = (1j) ** ny * zdiag(z)
    w = np.empty_like(v)
    w[b ^ x] = ph * v
    return float(np.real(v.conj() @ w))


def budget_needed(theta, obj, tol=0.1):
    ex = loss(theta, obj)
    for Nb in LADDER:
        if abs(surrogate_loss(theta, obj, Nb) - ex) <= tol:
            return Nb
    return None


def op_entanglement(theta, obj):
    """Operator entanglement (entropy, bits) of the Heisenberg-evolved
    objective across the middle cut."""
    O = np.zeros((DIM, DIM), dtype=complex)
    b = np.arange(DIM)
    for (x, z), c in obj.items():
        ny = int(x & z).bit_count()
        col = (1j) ** ny * zdiag(z)
        O[b ^ x, b] += c * col
    for (gx, gz, th) in reversed(gate_list(theta)):   # O -> U^dag O U
        ny = int(gx & gz).bit_count()
        ph = (1j) ** ny * zdiag(gz)
        PO = np.empty_like(O)
        PO[b ^ gx, :] = ph[:, None] * O
        OP = np.empty_like(O)
        OP[:, b ^ gx] = O * ph[None, :]
        POP = np.empty_like(PO)
        POP[:, b ^ gx] = PO * ph[None, :]
        c1, s1 = np.cos(th), np.sin(th)
        # e^{i th P} O e^{-i th P} = c^2 O + s^2 POP + i c s (PO - OP)
        O = c1 * c1 * O + s1 * s1 * POP + 1j * c1 * s1 * (PO - OP)
    half = DIM // (2 ** (N // 2))
    R = O.reshape(2 ** (N // 2), 2 ** (N // 2),
                  2 ** (N // 2), 2 ** (N // 2))
    R = np.transpose(R, (0, 2, 1, 3)).reshape(4 ** (N // 2), 4 ** (N // 2))
    s = np.linalg.svd(R, compute_uv=False)
    p = s ** 2
    p = p[p > 1e-14]
    p = p / p.sum()
    return float(-(p * np.log2(p)).sum())


OBJ = {"A_order": MST, "B_heating": dict(HTERMS)}


def run():
    rng = np.random.default_rng(20260718)
    rows = []
    base = {}
    for name, obj in OBJ.items():
        vals = []
        for _ in range(8):
            th = rng.uniform(-1.0, 1.0, K)
            vals.append((budget_needed(th, obj), op_entanglement(th, obj)))
        ns = [v[0] for v in vals if v[0]]
        base[name] = (float(np.median(ns)) if ns else None,
                      float(np.median([v[1] for v in vals])))
        print(f"baseline {name}: median N* = {base[name][0]}, "
              f"median S_op = {base[name][1]:.2f} bits "
              f"(range {min(v[1] for v in vals):.2f}"
              f"-{max(v[1] for v in vals):.2f})", flush=True)
    for name, obj in OBJ.items():
        th = 0.1 * rng.normal(size=K)
        for t in range(31):
            if t in (0, 10, 20, 30):
                lo = loss(th, obj)
                gn = float(np.linalg.norm(grad(th, obj)))
                nb = budget_needed(th, obj)
                so = op_entanglement(th, obj)
                rows.append(dict(obj=name, t=t, loss=lo, grad=gn,
                                 nstar=nb, s_op=so,
                                 base_n=base[name][0],
                                 base_s=base[name][1]))
                print(f"{name} t={t:>2} loss={lo:>8.4f} |grad|={gn:>7.3f} "
                      f"N*={str(nb):>6} S_op={so:>5.2f}", flush=True)
            if t < 30:
                th = th + 0.2 * grad(th, obj)          # ASCENT
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if not CSV.exists() or CSV.stat().st_size == 0:
            w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    print(f"n = {N}, K = {K} drive segments, T = {K * M_TROT * DT:.1f}, "
          f"E_min = {EMIN:.4f}, <H>_0 = {expect(PSI0, HTERMS):.4f}\n")
    run()
    print("\nPre-registered: K1 (sixth face) fires if trained N*/S_op stay")
    print("at/below the random-theta baseline for BOTH objectives; T6")
    print("survives if a physical objective drives them above baseline")
    print("and rising while gradients stay O(1).")
