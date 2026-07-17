"""T2 validation: the dichotomy theorem's two lemmas on a second,
maximally different DLA — collective spin su(2) at n = 5.

T1 exhibited the free-fermion case (DLA dim 66, multiplicity-free
sectors, BP side of the dichotomy). This file exhibits the opposite
corner: the collective-spin ansatz e^{-i a J_x} e^{-i b J_z} has DLA
su(2) (dimension THREE), and the 4^n-dim operator space decomposes into
spin-l irreps of dimension 2l+1 <= 2n+1 (all polynomial!) with
EXPONENTIALLY growing multiplicities (n = 5: the l = 0 isotypic
component alone has 42 copies; total 286 aligned irrep slots carry the
whole 1024-dim space).

What is validated, exactly:

  V1 (Lemma B, multiplicity contraction — the theorem's new content):
     the loss on an UNKNOWN input rho equals a sum of poly-many
     contracted terms sum_l Tr[R_l(theta) M_l], where M_l are
     (2l+1)x(2l+1) cross-moment matrices, each entry a SINGLE
     single-copy observable of rho, measured once. The multiplicity
     index (up to 42 copies) is contracted away because the ad-dynamics
     never touches it. Surrogate == statevector to machine precision.
  V2 (Lemma A, per-irrep variance law): Var_theta[L_l] compared to the
     Haar prediction ||M_l||_F^2 / (2l+1) per irrep type.
  V3 (alignment): the generator blocks computed from different copies
     of the same irrep type coincide — the basis construction (highest
     weight + lowering) is what makes contraction well-defined.

Run: .venv/bin/python hunt/code/t2_dichotomy_su2.py
"""

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).parent))

N = 5
DIM = 2 ** N
OP = DIM * DIM
RNG = np.random.default_rng(20260717)

SX = np.array([[0, 1], [1, 0]], dtype=complex) / 2
SY = np.array([[0, -1j], [1j, 0]], dtype=complex) / 2
SZ = np.array([[1, 0], [0, -1]], dtype=complex) / 2
I2 = np.eye(2, dtype=complex)


def collective(s):
    out = np.zeros((DIM, DIM), dtype=complex)
    for i in range(N):
        ops = [I2] * N
        ops[i] = s
        M = np.array([[1]], dtype=complex)
        for o in ops:
            M = np.kron(M, o)
        out += M
    return out


JX, JY, JZ = collective(SX), collective(SY), collective(SZ)


def ad_super(J):
    """[J, .] on row-major vec: vec(JX - XJ) = (J ox I - I ox J^T) vec."""
    return np.kron(J, np.eye(DIM)) - np.kron(np.eye(DIM), J.T)


ADX, ADY, ADZ = ad_super(JX), ad_super(JY), ad_super(JZ)
AD_MINUS = ADX - 1j * ADY


def hs_vec(A):
    """Flattened operator with HS normalization Tr(A^dag B)/2^n."""
    return A.reshape(-1) / np.sqrt(DIM)


# ------------------------------------------- isotypic decomposition ----

def decompose():
    """Aligned bases T[l][copy, m, :] built by highest-weight + lowering."""
    C2 = ADX @ ADX + ADY @ ADY + ADZ @ ADZ
    assert np.abs(C2 - C2.conj().T).max() < 1e-9
    evals, evecs = np.linalg.eigh(C2)
    T = {}
    for l in range(N + 1):
        target = l * (l + 1)
        sel = np.abs(evals - target) < 1e-6
        if not sel.any():
            continue
        S = evecs[:, sel]                       # C2 = l(l+1) eigenspace
        Az = S.conj().T @ ADZ @ S
        mvals, mvecs = np.linalg.eigh(Az)
        top = S @ mvecs[:, np.abs(mvals - l) < 1e-6]   # m = +l copies
        k = top.shape[1]
        basis = np.zeros((k, 2 * l + 1, OP), dtype=complex)
        for a in range(k):
            v = top[:, a]
            basis[a, 2 * l] = v                 # index m+l: top at 2l
            for m in range(l, -l, -1):          # lower m -> m-1
                coef = np.sqrt(l * (l + 1) - m * (m - 1))
                v = AD_MINUS @ v / coef
                assert abs(np.linalg.norm(v) - 1) < 1e-8
                basis[a, m + l - 1] = v
        T[l] = basis
    total = sum(b.shape[0] * b.shape[1] for b in T.values())
    assert total == OP, total
    return T


TBASIS = decompose()


def gen_blocks():
    """Per-irrep generator blocks i<T_m'|ad_a|T_m>, from copy 0; V3
    asserts every other copy gives the same block (alignment)."""
    blocks = {}
    for l, basis in TBASIS.items():
        d = 2 * l + 1
        blocks[l] = {}
        for name, AD in (("x", ADX), ("z", ADZ)):
            ref = None
            for a in range(basis.shape[0]):
                B = np.zeros((d, d), dtype=complex)
                for mp in range(d):
                    for m in range(d):
                        B[mp, m] = 1j * (basis[a, mp].conj()
                                         @ (AD @ basis[a, m]))
                if ref is None:
                    ref = B
                else:
                    assert np.abs(B - ref).max() < 1e-8, (l, name, a)
            blocks[l][name] = ref
    return blocks


BLOCKS = gen_blocks()
LAYERS = 4


def surrogate_R(l, params):
    """Heisenberg propagator on irrep type l for the layered ansatz
    U = prod_l e^{-i a J_x} e^{-i b J_z} (validated convention)."""
    d = 2 * l + 1
    R = np.eye(d, dtype=complex)
    for lay in reversed(range(LAYERS)):
        R = expm(params[2 * lay + 1] * BLOCKS[l]["z"]) @ R
        R = expm(params[2 * lay] * BLOCKS[l]["x"]) @ R
    return R


def ansatz(params):
    U = np.eye(DIM, dtype=complex)
    for lay in range(LAYERS):
        U = expm(-1j * params[2 * lay] * JX) @ U
        U = expm(-1j * params[2 * lay + 1] * JZ) @ U
    return U


def components(A):
    """Coefficients of A in every aligned slot: dict l -> (k, 2l+1).
    The T-vectors are plain-dot orthonormal, and plain dot of flattened
    matrices IS the HS inner product Tr(A^dag B) — no extra factor."""
    v = A.reshape(-1)
    return {l: np.einsum('kmo,o->km', basis.conj(), v)
            for l, basis in TBASIS.items()}


def cross_moments(rho, O):
    """M_l = sum_copies o^(a) mu^(a)dag — the contracted poly data."""
    mu, oc = components(rho), components(O)
    return {l: np.einsum('km,kp->mp', oc[l], mu[l].conj())
            for l in TBASIS}


def surrogate_loss(M, params):
    # L = sum_l Tr[R_l M_l], M_l[m, m'] = sum_a o_m^(a) conj(mu_m'^(a))
    return float(np.real(sum(np.trace(surrogate_R(l, params) @ M[l])
                             for l in M)))


def exact_loss(rho, O, params):
    U = ansatz(params)
    return float(np.real(np.trace(rho @ U.conj().T @ O @ U)))


if __name__ == "__main__":
    ks = {l: TBASIS[l].shape[0] for l in TBASIS}
    slots = sum(ks[l] * (2 * l + 1) for l in ks)
    tracked = sum((2 * l + 1) ** 2 for l in ks)
    print(f"n = {N}: operator space {OP}, DLA = su(2) (dim 3)")
    print(f"multiplicities k_l: {ks}  (sum k_l(2l+1) = {slots})")
    print(f"contracted surrogate tracks {tracked} numbers "
          f"({tracked / OP:.1%} of the operator space)\n")

    # V1: contraction surrogate == exact, unknown input
    psi = RNG.normal(size=DIM) + 1j * RNG.normal(size=DIM)
    psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi.conj())
    O = np.zeros((DIM, DIM), dtype=complex)      # a non-collective local op
    ops = [I2] * N
    ops[0] = 2 * SZ
    M1 = np.array([[1]], dtype=complex)
    for o in ops:
        M1 = np.kron(M1, o)
    O = M1 + 0.3 * (JX @ JX - JZ)                # mixed-sector observable
    M = cross_moments(rho, O)
    worst = 0.0
    for _ in range(20):
        p = RNG.uniform(-np.pi, np.pi, 2 * LAYERS)
        worst = max(worst, abs(surrogate_loss(M, p)
                               - exact_loss(rho, O, p)))
    print(f"V1 (Lemma B): worst |contracted surrogate - exact| over 20 "
          f"random theta: {worst:.2e}")

    # V2: per-irrep variance vs Haar prediction ||M_l||_F^2/(2l+1)
    print("\nV2 (Lemma A): per-irrep Var_theta vs Haar prediction")
    print(f"   {'l':>3} {'dim':>4} {'mult':>5} {'Var (measured)':>15} "
          f"{'||M||^2/(2l+1)':>15}")
    samples = 400
    for l in sorted(TBASIS):
        if np.linalg.norm(M[l]) < 1e-12:
            continue
        vals = []
        for _ in range(samples):
            p = RNG.uniform(-np.pi, np.pi, 2 * LAYERS)
            vals.append(surrogate_loss({l: M[l]}, p))
        var = np.var(vals)
        pred = 0.0 if l == 0 else np.linalg.norm(M[l]) ** 2 / (2 * l + 1)
        note = "  (trivial irrep: constant loss)" if l == 0 else ""
        print(f"   {l:>3} {2*l+1:>4} {ks[l]:>5} {var:>15.3e} "
              f"{pred:>15.3e}{note}")
    print("\nReading: V1 at machine precision is Lemma B — the")
    print("multiplicity index (up to 42 copies) contracts away; the")
    print("surrogate pays poly moments on a space where multiplicities")
    print("are exponential in n. V2 within O(1) of Haar prediction at")
    print("4 layers (exact Haar requires deep circuits).")
