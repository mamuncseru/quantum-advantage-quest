"""Every algorithm is a polynomial, so every cost is a degree.

The autopsy's table lists which polynomial gives which algorithm. That table
is the unification, but as printed it is a list of names. This file turns it
into numbers by *constructing* the approximations and measuring the degree
each one needs.

The payoff is a single observation, and it is the whole point of QSVT:

    Grover's sqrt(N), HHL's condition number kappa, and Hamiltonian
    simulation's evolution time t are the same quantity wearing three
    costumes — the degree of a polynomial.

Once you believe that, "is there a quantum advantage here?" factors cleanly:

    advantage = (a block-encoding classical sampling cannot imitate)
              x (a degree classically unaffordable)

and the two factors can be attacked separately. Tang attacked the first.
Hamiltonian simulation wins on the first and is cheap in the second. This
file computes both.

Run:  .venv/bin/python predecessors/09-qsvt/polynomial_cost.py
"""

from __future__ import annotations

import numpy as np


# ------------------------------------------- best polynomial of a degree ---

def chebyshev_basis(d, xs, parity=None):
    """Columns T_k(x) for k <= d, restricted to one parity if asked.

    QSP can only produce polynomials of a definite parity, so a degree
    budget spent on the wrong parity buys nothing — the basis has to respect
    that or the degrees come out optimistic.
    """
    ks = range(d + 1)
    if parity == "even":
        ks = [k for k in ks if k % 2 == 0]
    elif parity == "odd":
        ks = [k for k in ks if k % 2 == 1]
    th = np.arccos(np.clip(xs, -1, 1))
    return np.array([np.cos(k * th) for k in ks]).T


def best_approximation_error(target, xs, d, parity=None, weights=None):
    """Least-squares fit of `target` on `xs` by a degree-d polynomial.

    Least squares rather than a true minimax (Remez) fit, so the degrees
    reported here are mild *over*-estimates of the optimum. Stated because
    it matters: the conclusions below are about scaling, and an honest
    constant-factor slack in the wrong direction is safer than a fitted one
    in the right direction.
    """
    B = chebyshev_basis(d, xs, parity)
    w = np.ones_like(xs) if weights is None else weights
    coeffs, *_ = np.linalg.lstsq(B * w[:, None], target(xs) * w, rcond=None)
    return float(np.abs(B @ coeffs - target(xs)).max())


def min_degree(target, xs, eps, parity=None, dmax=4000):
    """Smallest degree whose best approximation is within eps. Bisected."""
    lo, hi = 1, 8
    while hi < dmax and best_approximation_error(target, xs, hi, parity) > eps:
        lo, hi = hi, hi * 2
    if hi >= dmax:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if best_approximation_error(target, xs, mid, parity) <= eps:
            hi = mid
        else:
            lo = mid + 1
    return lo


# --------------------------------------------- the four canonical targets --

def sign_domain(delta, n=1200):
    """[-1,-delta] u [delta,1] — the gap is where sign() is not approximated."""
    half = np.linspace(delta, 1.0, n // 2)
    return np.concatenate([-half[::-1], half])


def degree_for_sign(delta, eps=0.05):
    """Approximating sign(x) away from a gap of half-width delta.

    This is search / amplitude amplification. With delta = sqrt(M/N) the
    degree comes out proportional to 1/delta = sqrt(N/M) — Grover's query
    count, appearing as a polynomial degree rather than as an iteration
    count.
    """
    xs = sign_domain(delta)
    return min_degree(np.sign, xs, eps, parity="odd")


def degree_for_inverse(kappa, eps=0.05, n=1200):
    """Approximating 1/x on [1/kappa, 1], scaled to stay bounded by 1.

    This is HHL / linear systems, and the degree comes out proportional to
    kappa — the condition number, which is exactly the parameter HHL's
    runtime is quoted in.
    """
    half = np.linspace(1.0 / kappa, 1.0, n // 2)
    xs = np.concatenate([-half[::-1], half])
    target = lambda x: (1.0 / kappa) / x                       # noqa: E731
    return min_degree(target, xs, eps, parity="odd")


def degree_for_evolution(t, eps=1e-3, n=1500):
    """Approximating cos(tx) on [-1,1] — Hamiltonian simulation.

    The Jacobi-Anger expansion says the coefficients collapse past k ~ t, so
    the degree is t + O(log(1/eps)): *additive* in the precision, which is
    the exponential improvement qubitization is famous for.
    """
    xs = np.linspace(-1, 1, n)
    return min_degree(lambda x: np.cos(t * x), xs, eps, parity="even")


def degree_for_gibbs(beta, eps=1e-3, n=1500):
    """Approximating e^{-beta(x+1)/2} on [-1,1] — Gibbs state preparation,
    the polynomial hunting ground C runs on."""
    xs = np.linspace(-1, 1, n)
    return min_degree(lambda x: np.exp(-beta * (x + 1) / 2), xs, eps,
                      parity=None)


def fit_scaling(xs, ys):
    """Fitted exponent of y ~ x^a, for reporting how a degree grows."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    m = (xs > 0) & (ys > 0)
    return float(np.polyfit(np.log(xs[m]), np.log(ys[m]), 1)[0])


# ------------------------------- the other factor: is the encoding imitable?

def low_rank_imitability(A, rank, samples=None, seed=0):
    """How well a low-rank sketch reproduces A — the Tang-style attack.

    Quantum-inspired classical algorithms work when the block-encoded matrix
    can be replaced by a sample-built low-rank sketch. The relative error of
    the best rank-r truncation is the cleanest proxy: small means a
    classical algorithm can imitate the encoding and the quantum advantage
    evaporates, whatever the polynomial degree.
    """
    s = np.linalg.svd(A, compute_uv=False)
    return float(np.sqrt((s[rank:] ** 2).sum() / (s ** 2).sum()))


def stable_rank(A):
    """||A||_F^2 / ||A||_2^2 — how many directions actually carry weight."""
    s = np.linalg.svd(A, compute_uv=False)
    return float((s ** 2).sum() / s[0] ** 2)


def low_rank_matrix(dim, rank, seed=0):
    rng = np.random.default_rng(seed)
    U = rng.normal(size=(dim, rank))
    A = U @ U.T
    return A / np.linalg.norm(A, 2)


def sparse_local_matrix(dim, seed=0):
    """A sparse, full-rank matrix of the kind a local Hamiltonian gives."""
    rng = np.random.default_rng(seed)
    A = np.zeros((dim, dim))
    for i in range(dim - 1):
        A[i, i + 1] = A[i + 1, i] = 1.0
    A[np.arange(dim), np.arange(dim)] = rng.normal(size=dim) * 0.3
    return A / np.linalg.norm(A, 2)


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · THE SAME TABLE, WITH DEGREES INSTEAD OF NAMES\n")
    print("   search / amplitude amplification — sign(x) outside a gap δ\n")
    print(f"   {'gap δ':>10} {'≈ N (for δ=1/√N)':>18} {'degree':>9} "
          f"{'degree·δ':>11}")
    deltas = [0.25, 0.125, 0.0625, 0.03125]
    degs = []
    for delta in deltas:
        d = degree_for_sign(delta)
        degs.append(d)
        print(f"   {delta:>10.4f} {int(round(1 / delta ** 2)):>18} {d:>9} "
              f"{d * delta:>11.2f}")
    print(f"\n   degree ~ δ^{fit_scaling(deltas, degs):.2f} — i.e. ~1/δ = √N.")
    print("   **Grover's √N is a polynomial degree.** The 'iterations' of")
    print("   autopsy 06 were always the degree of an approximation to sign.\n")

    print("   linear systems — 1/x on [1/κ, 1]\n")
    print(f"   {'κ':>10} {'degree':>9} {'degree/κ':>11}")
    kappas = [4, 8, 16, 32]
    kdegs = []
    for kappa in kappas:
        d = degree_for_inverse(kappa)
        kdegs.append(d)
        print(f"   {kappa:>10} {d:>9} {d / kappa:>11.2f}")
    print(f"\n   degree ~ κ^{fit_scaling(kappas, kdegs):.2f} — HHL's condition")
    print("   number is a polynomial degree too.\n")

    print("   Hamiltonian simulation — cos(tx) on [-1, 1]\n")
    print(f"   {'t':>10} {'degree':>9} {'degree − t':>12}")
    ts = [4, 8, 16, 32, 64, 128]
    tdegs = []
    for t in ts:
        d = degree_for_evolution(t)
        tdegs.append(d)
        print(f"   {t:>10} {d:>9} {d - t:>12}")
    print("\n   Read the third column, not a power law: degree − t is nearly")
    print("   constant, so degree = t + O(log 1/ε). That ADDITIVE offset is")
    print("   the Jacobi-Anger expansion, and it is exactly the αt + log(1/ε)")
    print("   of autopsy 09 arrived at from the polynomial side. (A naive")
    print(f"   log-log fit reports t^{fit_scaling(ts, tdegs):.2f} here, which is an artefact")
    print("   of the additive term at small t — worth noticing, because it is")
    print("   the kind of fit that turns an additive law into a fake")
    print("   sublinear one.)\n")

    print("   how each one responds to demanding more precision\n")
    print(f"   {'ε':>10} {'sign (δ=1/8)':>14} {'1/x (κ=8)':>12} "
          f"{'cos(8x)':>10}")
    for eps in (1e-1, 1e-2, 1e-3, 1e-4):
        print(f"   {eps:>10.0e} {degree_for_sign(0.125, eps):>14} "
              f"{degree_for_inverse(8, eps):>12} "
              f"{degree_for_evolution(8, eps):>10}")
    print("\n   Simulation's degree barely moves; the other two climb. That")
    print("   difference — additive versus multiplicative in log(1/ε) — is")
    print("   the whole reason simulation is the healthiest application.\n")

    print("2 · THE OTHER FACTOR: CAN THE ENCODING BE IMITATED?\n")
    dim = 128
    print(f"   {'matrix':>28} {'stable rank':>13} "
          f"{'error of rank-8 sketch':>24}")
    for name, A in (("low-rank data (rank 8)", low_rank_matrix(dim, 8)),
                    ("low-rank data (rank 32)", low_rank_matrix(dim, 32)),
                    ("sparse local Hamiltonian", sparse_local_matrix(dim))):
        print(f"   {name:>28} {stable_rank(A):>13.1f} "
              f"{low_rank_imitability(A, 8):>24.3f}")
    print("\n   A rank-8 sketch reproduces the low-rank matrix exactly and")
    print("   the sparse Hamiltonian not at all. That is the difference")
    print("   between an advantage Tang can dequantise and one nobody can:")
    print("   it is a property of the ENCODING, and it is decided before")
    print("   any polynomial is chosen.\n")

    print("3 · THE FACTORISATION, STATED\n")
    print("   advantage = (encoding classical sampling cannot imitate)")
    print("             × (degree classically unaffordable)")
    print()
    print(f"   {'algorithm':>26} {'encoding':>22} {'degree':>22}")
    rows = [("Grover / search", "oracle — not imitable", "√N — but only quadratic"),
            ("HHL on low-rank data", "IMITABLE (Tang)", "κ"),
            ("HHL on sparse systems", "not imitable", "κ"),
            ("Hamiltonian simulation", "not imitable", "αt + log(1/ε) — cheap"),
            ("Gibbs sampling", "not imitable", "β / spectral gap")]
    for a, b, c in rows:
        print(f"   {a:>26} {b:>22} {c:>22}")
    print("\n   Read the table as a checklist: an advantage claim has to win")
    print("   BOTH columns. Grover wins the first and loses the second;")
    print("   low-rank HHL wins the second and loses the first; simulation")
    print("   wins both, which is why it is the one that survived.")


if __name__ == "__main__":
    _demo()
