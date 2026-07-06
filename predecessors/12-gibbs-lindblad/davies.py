"""Davies generator — the textbook quantum Gibbs sampler, built explicitly.

The obstruction Davies resolves: quantum Metropolis needs to compare
energies, but measuring energy destroys the coherences a quantum state
needs. Davies' construction (weak-coupling limit): decompose each coupling
operator A into Bohr-frequency components

    A(omega) = sum_{E_k - E_j = omega} |j><j| A |k><k|      (jumps of energy omega)

and give each a Glauber rate gamma(omega) = 1/(1 + e^{-beta omega}), which
satisfies the KMS/detailed-balance condition gamma(omega) = e^{beta omega}
gamma(-omega). The resulting Lindbladian fixes the Gibbs state EXACTLY and
(for ergodic couplings) converges to it with a spectral gap.

The catch that kept this a thought experiment: A(omega) requires exactly
resolving all Bohr frequencies — fine at 3 qubits (here), an oracle
assumption at 300. The CKG 2023 samplers are the modern fix (Gaussian-
filtered jumps + an explicit coherent correction term, exact detailed
balance without perfect energy resolution). Same skeleton, honest cost.
"""

import numpy as np
from scipy.linalg import expm

from qsim import I2, X, Y, Z


def kron_chain(ops):
    M = np.array([[1.0 + 0j]])
    for op in ops:
        M = np.kron(M, op)
    return M


def site_op(op, i, n):
    return kron_chain([op if j == i else I2 for j in range(n)])


def heisenberg_with_fields(n=3, seed=1):
    """Heisenberg chain + random z-fields: generic, nondegenerate spectrum."""
    rng = np.random.default_rng(seed)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            H += site_op(P, i, n) @ site_op(P, i + 1, n)
    for i in range(n):
        H += rng.normal(0, 0.7) * site_op(Z, i, n)
    return H


def gibbs_state(H, beta):
    lam, V = np.linalg.eigh(H)
    w = np.exp(-beta * (lam - lam.min()))
    return (V * (w / w.sum())) @ V.conj().T


def bohr_components(A, H, tol=1e-9):
    """Split coupling A into jump operators A(omega), omega = E_k - E_j."""
    lam, V = np.linalg.eigh(H)
    At = V.conj().T @ A @ V
    comps = {}
    for j in range(len(lam)):
        for k in range(len(lam)):
            if abs(At[j, k]) < tol:
                continue
            omega = lam[k] - lam[j]
            key = round(omega / tol) * tol
            comps.setdefault(key, np.zeros_like(At))[j, k] += At[j, k]
    # back to the computational basis
    return {w: V @ M @ V.conj().T for w, M in comps.items()}


def davies_superoperator(H, couplings, beta):
    """Vectorized Lindbladian (row-major vec: vec(X rho Y) = (X kron Y^T) vec)."""
    d = H.shape[0]
    Id = np.eye(d)
    L = np.zeros((d * d, d * d), dtype=complex)
    gamma = lambda w: 1.0 / (1.0 + np.exp(-beta * w))   # gamma(w)=e^{bw}gamma(-w)
    for A in couplings:
        for w, Aw in bohr_components(A, H).items():
            AdA = Aw.conj().T @ Aw
            L += gamma(w) * (np.kron(Aw, Aw.conj())
                             - 0.5 * np.kron(AdA, Id)
                             - 0.5 * np.kron(Id, AdA.T))
    return L


def spectral_gap(L):
    ev = np.linalg.eigvals(L)
    re = np.sort(ev.real)[::-1]
    assert re[0] > -1e-9, "no stationary state?"
    return -re[1]


if __name__ == "__main__":
    n, beta = 3, 1.0
    H = heisenberg_with_fields(n)
    couplings = [site_op(X, i, n) for i in range(n)] + \
                [site_op(Y, i, n) for i in range(n)]
    L = davies_superoperator(H, couplings, beta)
    rho_beta = gibbs_state(H, beta)

    print(f"n = {n} qubits, beta = {beta}")
    print(f"||L(rho_beta)|| = {np.linalg.norm(L @ rho_beta.reshape(-1)):.2e}"
          "  (Gibbs is stationary)")
    print(f"spectral gap    = {spectral_gap(L):.4f}  (mixing time ~ 1/gap)")

    rho = np.eye(2 ** n, dtype=complex) / 2 ** n        # start: maximally mixed
    for t in (0.0, 1.0, 3.0, 10.0, 30.0):
        rho_t = (expm(L * t) @ rho.reshape(-1)).reshape(2 ** n, 2 ** n)
        dist = 0.5 * np.abs(np.linalg.eigvalsh(rho_t - rho_beta)).sum()
        print(f"  t = {t:5.1f}: trace distance to Gibbs = {dist:.6f}")
