"""T1 first numerics: the module dichotomy for trainable circuits on
UNKNOWN quantum data — is the gradient-alive sector always the
classically-trackable sector?

Setting (exactly solvable on purpose): the TFIM ansatz
U(theta) = prod_l e^{-i b_l sum Z_i} e^{-i a_l sum X_i X_{i+1}} has a
polynomial dynamical Lie algebra — under Jordan-Wigner both generators
are Majorana quadratics (X_i X_{i+1} = -i c_{2i+1} c_{2i+2},
Z_i = -i c_{2i} c_{2i+1}; note sum X_i would NOT be — a first draft of
this file used the wrong TFIM and every check failed, which is exactly
what the checks are for). The DLA lives in the quadratics
span{i c_a c_b}, dimension 2n^2 - n = 66 at n = 6. Operator space splits
into ad-invariant Majorana-degree sectors (even degree 2k,
dim C(2n, 2k)); the ansatz acts block-diagonally on them.

Experiments, all exact statevector (n = 6):

  A  g-sim exhibit: for a module observable on an UNKNOWN input, the
     loss is a linear functional of the 66 input moments <i c_a c_b>,
     measured once (single-copy), reused for every theta. Machine-
     precision agreement = kill K1 fires at the free-fermion point.
  B  the variance law, inputs fixed: per-sector gradient variance
     Var_theta[grad] next to the input's sector mass — for a physical
     (product) input and for one fixed Haar state. The dichotomy at
     scale rides on this law: trainability of a sector is paid for by
     input mass in that sector, and low sectors are the trackable ones.
  C  interleaved black-box: a fixed unknown scrambler U between the two
     trainable halves leaks the observable into high sectors. Measured
     vs depth: module mass, sector budget for 95% of the operator, and
     gradient variance on both sides of the box (input fixed |0^n>).
  D  block surrogate: the classical competitor that learns only the
     66x66 degree-2 block of Ad_U (poly queries). Its loss error vs
     depth, next to the gradient scale — where gradients live and the
     block error is comparable, the linear-loss window is closed.

Run: .venv/bin/python hunt/code/t1_module_dichotomy.py   (~2 min)
"""

import sys
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).parent))

N = 6
DIM = 2 ** N
RNG = np.random.default_rng(20260717)

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def kron(ops):
    out = np.array([[1]], dtype=complex)
    for o in ops:
        out = np.kron(out, o)
    return out


def site(op, i):
    return kron([op if j == i else I2 for j in range(N)])


# ------------------------------------------------- Majorana machinery ----

def majoranas():
    cs = []
    for i in range(N):
        tail = [Z] * i
        cs.append(kron(tail + [X] + [I2] * (N - i - 1)))
        cs.append(kron(tail + [Y] + [I2] * (N - i - 1)))
    return cs


CS = majoranas()


def monomial(idx):
    """Hermitian, HS-normalized Majorana monomial for an even index set."""
    M = np.eye(DIM, dtype=complex)
    for a in idx:
        M = M @ CS[a]
    return M * (1j) ** (len(idx) * (len(idx) - 1) // 2)


DEGREES = list(range(0, 2 * N + 1, 2))
SECTOR_IDX = {d: list(combinations(range(2 * N), d)) for d in DEGREES}
DEG2 = [monomial(idx) for idx in SECTOR_IDX[2]]        # the module, dim 66


def hs(a, b):
    return np.trace(a.conj().T @ b) / DIM


def degree_mass(O):
    """|coeff|^2 of O per Majorana degree (exact projection)."""
    return {d: sum(abs(hs(monomial(idx), O)) ** 2 for idx in SECTOR_IDX[d])
            for d in DEGREES}


# ------------------------------------------------------------ ansatz ----

HXX = sum(site(X, i) @ site(X, i + 1) for i in range(N - 1))
HZ = sum(site(Z, i) for i in range(N))
LAYERS = 4


def ansatz(params):
    # param 0 is an XX angle so |0^n> is not an eigenstate of layer one
    U = np.eye(DIM, dtype=complex)
    for l in range(LAYERS):
        U = expm(-1j * params[2 * l] * HXX) @ U
        U = expm(-1j * params[2 * l + 1] * HZ) @ U
    return U


def rand_params():
    return RNG.uniform(-np.pi, np.pi, 2 * LAYERS)


def rand_state(rng=None):
    r = rng or RNG
    v = r.normal(size=DIM) + 1j * r.normal(size=DIM)
    return v / np.linalg.norm(v)


def loss(psi, U, O):
    w = U @ psi
    return float(np.real(w.conj() @ O @ w))


def grad0(psi, O, params, h=1e-5):
    p1, p2 = params.copy(), params.copy()
    p1[0] += h
    p2[0] -= h
    return (loss(psi, ansatz(p1), O) - loss(psi, ansatz(p2), O)) / (2 * h)


# ------------------------------------------------ A: g-sim surrogate ----

def ad_matrix(H):
    """The map B -> i[H, B] on the degree-2 module (66x66, antisymmetric)."""
    A = np.zeros((66, 66))
    for k, Bk in enumerate(DEG2):
        C = 1j * (H @ Bk - Bk @ H)
        for j, Bj in enumerate(DEG2):
            A[j, k] = np.real(hs(Bj, C))
    return A


AXX, AZ = ad_matrix(HXX), ad_matrix(HZ)


def heisenberg_coeffs(o, params):
    """Coefficients of U(params)^dag O U(params), O = sum o_j B_j."""
    coeff = o.copy()
    for l in reversed(range(LAYERS)):
        coeff = expm(params[2 * l + 1] * AZ) @ coeff
        coeff = expm(params[2 * l] * AXX) @ coeff
    return coeff


def gsim_exhibit(trials=20):
    O = site(Z, 0)
    o = np.array([np.real(hs(B, O)) for B in DEG2])
    worst = 0.0
    for _ in range(trials):
        psi, params = rand_state(), rand_params()
        m = np.array([np.real(psi.conj() @ B @ psi) for B in DEG2])
        worst = max(worst, abs(float(heisenberg_coeffs(o, params) @ m)
                               - loss(psi, ansatz(params), O)))
    return worst


# --------------------------------------------- B: the variance law ----

def variance_law(samples=60, per_sector=12):
    """Fixed inputs; Var over theta only, next to input sector mass."""
    inputs = {
        "|0^n>": np.eye(DIM, dtype=complex)[:, 0],
        "Haar (fixed)": rand_state(np.random.default_rng(7)),
    }
    out = {}
    for name, psi in inputs.items():
        rho = np.outer(psi, psi.conj())
        rmass = degree_mass(rho)
        tot = sum(rmass.values())
        rows = []
        for d in DEGREES[1:]:
            idxs = SECTOR_IDX[d]
            picks = [idxs[i] for i in
                     RNG.choice(len(idxs), min(per_sector, len(idxs)),
                                replace=False)]
            grads = []
            for idx in picks:
                O = monomial(idx)
                for _ in range(max(1, samples // len(picks))):
                    grads.append(grad0(psi, O, rand_params()))
            rows.append((d, len(idxs), rmass[d] / tot,
                         float(np.var(grads))))
        out[name] = rows
    return out


# ------------------------------------------- C/D: interleaved box ----

def embed_pair(q, i, j):
    """Embed a 4x4 gate on (possibly nonadjacent) qubits i < j."""
    swap = np.eye(DIM, dtype=complex)
    if j != i + 1:
        # bring j next to i via a permutation of basis states
        perm = np.arange(DIM)
        for b in range(DIM):
            bit_j = (b >> (N - 1 - j)) & 1
            bit_a = (b >> (N - 1 - (i + 1))) & 1
            nb = b & ~((1 << (N - 1 - j)) | (1 << (N - 1 - (i + 1))))
            nb |= bit_j << (N - 1 - (i + 1))
            nb |= bit_a << (N - 1 - j)
            perm[b] = nb
        swap = np.eye(DIM, dtype=complex)[perm]
    pre = np.eye(2 ** i, dtype=complex)
    post = np.eye(2 ** (N - i - 2), dtype=complex)
    G = np.kron(np.kron(pre, q), post)
    return swap.conj().T @ G @ swap


def box(depth, rng, local=True):
    """Unknown scrambler: local brickwork, or nonlocal random pairs."""
    U = np.eye(DIM, dtype=complex)
    for layer in range(depth):
        if local:
            pairs = [(i, i + 1) for i in range(layer % 2, N - 1, 2)]
        else:
            order = rng.permutation(N)
            pairs = [tuple(sorted((order[2 * k], order[2 * k + 1])))
                     for k in range(N // 2)]
        L = np.eye(DIM, dtype=complex)
        for (i, j) in pairs:
            g = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
            q, _ = np.linalg.qr(g)
            L = embed_pair(q, i, j) @ L
        U = L @ U
    return U


def interleaved_scan(depths=(0, 1, 2, 3, 4, 6), samples=30, local=True):
    O = site(Z, 0)
    o2 = np.array([np.real(hs(B, O)) for B in DEG2])
    psi = np.eye(DIM, dtype=complex)[:, 0]              # fixed |0^n>
    m = np.array([np.real(psi.conj() @ B @ psi) for B in DEG2])
    rows = []
    for d in depths:
        rng = np.random.default_rng(1000 + d)
        U = box(d, rng, local=local)
        OU = U.conj().T @ O @ U
        mass = degree_mass(OU)
        tot = sum(mass.values())
        m2 = (mass[0] + mass[2]) / tot
        cum, budget = 0.0, 0
        for deg in DEGREES:
            cum += mass[deg] / tot
            budget += comb(2 * N, deg)
            if cum >= 0.95:
                break
        T = np.zeros((66, 66))                          # deg-2 block of Ad_U
        for k, Bk in enumerate(DEG2):
            BU = U.conj().T @ Bk @ U
            for j, Bj in enumerate(DEG2):
                T[j, k] = np.real(hs(Bj, BU))
        gth, gph, errs, scale = [], [], [], []
        for _ in range(samples):
            th, ph = rand_params(), rand_params()
            V1 = ansatz(th)
            full_loss = loss(psi, ansatz(ph) @ U @ V1, O)
            h = 1e-5
            for arr, out in ((th, gth), (ph, gph)):
                p1, p2 = arr.copy(), arr.copy()
                p1[0] += h
                p2[0] -= h
                if arr is th:
                    l1 = loss(psi, ansatz(ph) @ U @ ansatz(p1), O)
                    l2 = loss(psi, ansatz(ph) @ U @ ansatz(p2), O)
                else:
                    l1 = loss(psi, ansatz(p1) @ U @ V1, O)
                    l2 = loss(psi, ansatz(p2) @ U @ V1, O)
                out.append((l1 - l2) / (2 * h))
            coeff = heisenberg_coeffs(o2, ph)           # through V2
            coeff = T @ coeff                           # through the box
            coeff = heisenberg_coeffs(coeff, th)        # through V1
            errs.append(abs(float(coeff @ m) - full_loss))
            scale.append(abs(full_loss))
        rows.append(dict(d=d, m2=m2, budget=budget,
                         var_th=float(np.var(gth)),
                         var_ph=float(np.var(gph)),
                         block_err=float(np.mean(errs)),
                         loss_scale=float(np.mean(scale))))
    return rows


# ------------------------------------------- E: ad-closure dimension ----

def ad_closure_dim(U, cap=1900):
    """Dimension of the smallest ad_g-invariant operator subspace
    containing Ad_U(module) — the space a training-orbit surrogate must
    track. Grown by commutators with the ansatz generators, orthonormal
    basis kept explicitly; even-parity sector has dimension 2048."""
    basis = []          # list of flattened orthonormal operator vectors
    mats = []           # same elements as 64x64 matrices

    def add(Mat):
        v = Mat.reshape(-1)
        for q in basis:
            v = v - (q.conj() @ v) * q
        nrm = np.linalg.norm(v)
        if nrm > 1e-8:
            v = v / nrm
            basis.append(v)
            mats.append(v.reshape(DIM, DIM))
            return True
        return False

    for B in DEG2:
        add(U.conj().T @ B @ U)
    frontier = list(mats)
    while frontier and len(basis) < cap:
        new_frontier = []
        for Mat in frontier:
            for H in (HXX, HZ):
                C = 1j * (H @ Mat - Mat @ H)
                if add(C):
                    new_frontier.append(mats[-1])
            if len(basis) >= cap:
                break
        frontier = new_frontier
    return len(basis), len(basis) >= cap


if __name__ == "__main__":
    print(f"n = {N}, TFIM-DLA ansatz ({LAYERS} layers), module dim 66\n")

    print("A. g-sim from 66 single-copy moments vs on-device loss")
    print(f"   worst |surrogate - exact| over 20 random (psi, theta): "
          f"{gsim_exhibit():.2e}")
    print("   moments measured ONCE, reused for every theta -> K1 fires "
          "at the free-fermion point\n")

    print("B. the variance law: Var_theta[grad] vs input sector mass")
    for name, rows in variance_law().items():
        print(f"   input {name}:")
        print(f"   {'degree':>7} {'dim':>5} {'input mass':>11} "
              f"{'Var_theta[grad]':>16}")
        for d, dim, mass, v in rows:
            print(f"   {d:>7} {dim:>5} {mass:>11.3f} {v:>16.2e}")

    for local, tag in ((True, "local brickwork (lightcone-limited)"),
                       (False, "NONLOCAL random pairs (the live case)")):
        print(f"\nC/D. interleaved unknown scrambler — {tag}, "
              f"input |0^n> fixed")
        print(f"   {'depth':>6} {'mass<=2':>8} {'95% budget':>11} "
              f"{'Var grad th':>12} {'Var grad ph':>12} {'block err':>10} "
              f"{'|loss|':>8}")
        for r in interleaved_scan(local=local):
            print(f"   {r['d']:>6} {r['m2']:>8.3f} {r['budget']:>11} "
                  f"{r['var_th']:>12.2e} {r['var_ph']:>12.2e} "
                  f"{r['block_err']:>10.2e} {r['loss_scale']:>8.3f}")

    print("\nE. ad-closure of Ad_U(module): the space any training-orbit")
    print("   surrogate must track (even-parity operator space = 2048)")
    print(f"   {'box':>22} {'depth':>6} {'closure dim':>12}")
    for local, tag in ((True, "local"), (False, "nonlocal")):
        for d in (0, 1, 2):
            U = box(d, np.random.default_rng(1000 + d), local=local)
            dim, capped = ad_closure_dim(U)
            note = "+ (capped)" if capped else ""
            print(f"   {tag:>22} {d:>6} {dim:>12}{note}")
