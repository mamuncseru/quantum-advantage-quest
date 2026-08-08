"""QSP with actual phases — the half of the mechanism the demo skips.

`qsvt_demo.py` shows that d applications of the walk operator give the
Chebyshev polynomial T_d. That is QSP with every phase set to zero. The
*point* of QSP is that inserting rotations between the applications sweeps
out essentially every bounded polynomial of the right parity — "choosing
phases is choosing your algorithm".

So this file chooses them. It builds the QSP product

    U(x) = e^{i phi_0 Z} * prod_k [ W(x) e^{i phi_k Z} ],
    W(x) = [[x, i sqrt(1-x^2)], [i sqrt(1-x^2), x]]

verifies that <0|U|0> really is a degree-d polynomial of the stated parity,
solves for the phases that hit a requested target, and then measures the
thing nobody advertises: **how badly phase-finding conditions as the degree
grows**. That last number is the difference between a theorem and a
subroutine you can run.

Run:  .venv/bin/python predecessors/09-qsvt/qsp_phases.py
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def signal_operator(x):
    """W(x): the single-qubit rotation that carries the signal.

    Its eigenphases are +-arccos(x), which is why d applications produce a
    degree-d polynomial: the angles simply add.
    """
    s = np.sqrt(max(0.0, 1.0 - x * x))
    return np.array([[x, 1j * s], [1j * s, x]], dtype=complex)


def qsp_unitary(phases, x):
    """e^{i phi_0 Z} prod_k W(x) e^{i phi_k Z} — the whole QSP construction."""
    U = np.diag([np.exp(1j * phases[0]), np.exp(-1j * phases[0])])
    for phi in phases[1:]:
        U = U @ signal_operator(x) @ np.diag(
            [np.exp(1j * phi), np.exp(-1j * phi)])
    return U


def qsp_response(phases, xs):
    """Re<0|U(x)|0> for each x — the polynomial the circuit implements.

    Batched over x: the whole product is carried as an array of 2x2 blocks,
    which makes degree-100 phase searches affordable. `qsp_unitary` above is
    the same computation written for one x, and the tests check they agree.
    """
    xs = np.atleast_1d(np.asarray(xs, dtype=float))
    s = np.sqrt(np.maximum(0.0, 1.0 - xs * xs))
    W = np.empty((xs.size, 2, 2), dtype=complex)
    W[:, 0, 0] = xs
    W[:, 1, 1] = xs
    W[:, 0, 1] = 1j * s
    W[:, 1, 0] = 1j * s
    e = np.exp(1j * phases[0])
    U = np.zeros((xs.size, 2, 2), dtype=complex)
    U[:, 0, 0] = e
    U[:, 1, 1] = np.conj(e)
    for phi in phases[1:]:
        R = np.zeros((2, 2), dtype=complex)
        R[0, 0] = np.exp(1j * phi)
        R[1, 1] = np.exp(-1j * phi)
        U = U @ W @ R
    return U[:, 0, 0].real


def degree(phases):
    """d = number of signal applications = len(phases) - 1."""
    return len(phases) - 1


# ------------------------------------------------------ what QSP can hit ---

def chebyshev(d, xs):
    return np.cos(d * np.arccos(np.clip(xs, -1, 1)))


def check_parity(phases, xs=None, tol=1e-9):
    """A degree-d QSP response has parity d mod 2 — always, by construction.

    Verified rather than assumed, because parity is the constraint that
    decides which targets are reachable at all: you cannot approximate an
    even function with an odd-degree QSP.
    """
    xs = np.linspace(-0.99, 0.99, 41) if xs is None else xs
    p_plus = qsp_response(phases, xs)
    p_minus = qsp_response(phases, -xs)
    d = degree(phases)
    return bool(np.abs(p_plus - (-1) ** d * p_minus).max() < tol)


def fit_degree(phases, xs=None):
    """Recover the polynomial degree of the response by Chebyshev fitting.

    Confirms that the circuit really produces a *polynomial* of the claimed
    degree, rather than something that merely looks smooth.
    """
    xs = np.linspace(-0.98, 0.98, 400) if xs is None else xs
    y = qsp_response(phases, xs)
    d = degree(phases)
    basis = np.array([chebyshev(k, xs) for k in range(d + 1)]).T
    coeffs, *_ = np.linalg.lstsq(basis, y, rcond=None)
    resid = np.abs(basis @ coeffs - y).max()
    nonzero = [k for k, c in enumerate(coeffs) if abs(c) > 1e-6]
    return dict(coeffs=coeffs, residual=float(resid),
                highest=max(nonzero) if nonzero else 0)


# ------------------------------------------------------- finding phases ----

def solve_phases(target, d, xs=None, seed=0, tries=2, max_nfev=None):
    """Least-squares search for phases whose response matches `target`.

    This is the honest version of "choosing phases is choosing your
    algorithm": the choosing is a non-convex optimisation from a random
    start, and the returned residual says whether it succeeded. Production
    implementations use dedicated methods (Haah's, or Prony/Wilson-style
    factorisations) — not because the map is ill-conditioned (see
    `phase_map_spectrum`, which shows it is not) but because a generic
    non-convex search gets expensive long before the degrees real algorithms
    need.
    """
    xs = np.linspace(-0.99, 0.99, max(4 * d, 60)) if xs is None else xs
    want = np.array([target(float(x)) for x in xs])
    best = None
    for k in range(tries):
        rng = np.random.default_rng(seed + k)
        x0 = rng.uniform(-np.pi / 2, np.pi / 2, d + 1)
        res = least_squares(
            lambda p: qsp_response(p, xs) - want, x0,
            method="trf", max_nfev=max_nfev or 300 * (d + 1))
        if best is None or res.cost < best.cost:
            best = res
    return best.x, float(np.abs(qsp_response(best.x, xs) - want).max())


def phase_map_spectrum(d, xs=None, h=1e-6):
    """Singular values of d(response)/d(phases) at the exact T_d solution.

    Measures how invertible the phase -> polynomial map is. Two things fall
    out, and the second corrects a widespread impression:

    * exactly **one** singular value is zero, at every degree. That is a
      genuine gauge freedom of the QSP construction, not a numerical
      accident, and any phase-finding routine has to quotient it out.
    * modulo that direction the map is only *mildly* ill-conditioned, and
      the conditioning grows slowly with d — not exponentially. So the
      difficulty of high-degree phase finding is not local conditioning.
    """
    xs = np.linspace(-0.99, 0.99, 4 * d + 40) if xs is None else xs
    p0 = np.zeros(d + 1)
    base = qsp_response(p0, xs)
    J = np.empty((xs.size, d + 1))
    for k in range(d + 1):
        p = p0.copy()
        p[k] += h
        J[:, k] = (qsp_response(p, xs) - base) / h
    return np.linalg.svd(J, compute_uv=False)


def gauge_dimension(d, tol=1e-10):
    """How many exactly-flat directions the phase map has. Measured as 1."""
    s = phase_map_spectrum(d)
    return int((s < tol * s[0]).sum())


def conditioning_modulo_gauge(d, tol=1e-10):
    """Condition number after discarding the gauge direction."""
    s = phase_map_spectrum(d)
    nz = s[s > tol * s[0]]
    return float(nz[0] / nz[-1])


def phase_finding_conditioning(degrees=(4, 8, 16, 32)):
    """(degree, gauge dimension, conditioning modulo gauge) for each degree."""
    return [(d, gauge_dimension(d), conditioning_modulo_gauge(d))
            for d in degrees]


# ------------------------------------------- the algorithms, as polynomials

def poly_error(target, phases, xs=None):
    xs = np.linspace(-0.99, 0.99, 400) if xs is None else xs
    want = np.array([target(float(x)) for x in xs])
    return float(np.abs(qsp_response(phases, xs) - want).max())


def _demo():
    print("1 · ZERO PHASES REPRODUCE THE CHEBYSHEV DEMO\n")
    xs = np.linspace(-0.99, 0.99, 200)
    for d in (1, 2, 3, 5):
        phases = np.zeros(d + 1)
        err = np.abs(qsp_response(phases, xs) - chebyshev(d, xs)).max()
        print(f"   d = {d}: max |response - T_d| = {err:.2e}"
              f"   parity ok: {check_parity(phases)}")
    print("\n   which is the qsvt_demo.py result, recovered as the special")
    print("   case where every rotation is the identity.\n")

    print("2 · NON-ZERO PHASES GIVE OTHER POLYNOMIALS\n")
    rng = np.random.default_rng(1)
    for d in (3, 4, 6):
        phases = rng.uniform(-1, 1, d + 1)
        info = fit_degree(phases)
        print(f"   d = {d}: response is a polynomial of degree "
              f"{info['highest']}, parity {'odd' if d % 2 else 'even'} "
              f"({check_parity(phases)}), fit residual {info['residual']:.1e}")
    print("\n   Every reachable response is a bounded polynomial of parity")
    print("   d mod 2. That constraint — not the degree — is what decides")
    print("   which algorithms are expressible at a given cost.\n")

    print("3 · SOLVING FOR PHASES, AND WHAT IS ACTUALLY HARD ABOUT IT\n")
    print("   Small degrees: the naive least-squares search just works.\n")
    print(f"   {'degree d':>10} {'residual':>14}")
    for d in (2, 4, 6, 8, 10):
        _, resid = solve_phases(
            lambda x, d=d: chebyshev(d, np.array([x]))[0], d, tries=1)
        print(f"   {d:>10} {resid:>14.2e}")

    print("\n   Is the map ill-conditioned? Measure it directly — the")
    print("   Jacobian of response-with-respect-to-phases, at the exact")
    print("   solution:\n")
    print(f"   {'degree d':>10} {'zero directions':>17} "
          f"{'condition number modulo those':>32}")
    for d, gauge, cond in phase_finding_conditioning():
        print(f"   {d:>10} {gauge:>17} {cond:>32.2e}")
    print("\n   Exactly ONE flat direction at every degree — a real gauge")
    print("   freedom of the construction, which every phase-finding routine")
    print("   has to quotient out. And modulo it the conditioning grows only")
    print("   slowly, so the map is NOT the obstacle.")
    print("\n   What is the obstacle, then? The search. A generic non-convex")
    print("   solve from a random start becomes expensive well before the")
    print("   degrees §1 of polynomial_cost.py says real algorithms need")
    print("   (hundreds to thousands). That is why dedicated phase-finding")
    print("   algorithms exist — a cost of doing business that the phrase")
    print("   'choosing phases is choosing your algorithm' hides completely.")


if __name__ == "__main__":
    _demo()
