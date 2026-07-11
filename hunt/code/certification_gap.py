"""L9 first numerics: learning a physical model is single-copy-easy;
CERTIFYING it is memory-bound.

Construction: rho = Gibbs state of a local H (n=6); rho_bad = rho + c*W
with W a weight-n Pauli. Every marginal on < n qubits is IDENTICAL
(partial trace annihilates a full-weight Pauli), so every marginal-based
learner - including the AAKS max-entropy fit - outputs the same model
for both and reports zero misfit. Yet the states differ at trace
distance ~ c/  and the difference is detected by a two-copy purity/overlap
test at O(1/c^2) shots, while single-copy shadows pay 2^Theta(n).

Certification, not learning, is where quantum memory earns its keep on
physical data - and misspecification hiding in high weight is exactly
what device diagnostics must fear.

Run: .venv/bin/python hunt/code/certification_gap.py
"""

import importlib.util
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from qsim import X as PX, Y as PY, Z as PZ  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "davies", ROOT / "predecessors/12-gibbs-lindblad/davies.py")
davies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(davies)

N, BETA = 6, 0.3          # high T so lambda_min is macroscopic
Ypauli = np.array([[0, -1j], [1j, 0]])


def gibbs_state_beta(n, beta, seed):
    rng = np.random.default_rng(seed)
    field = rng.uniform(-1, 1, size=n)
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (PX, PY, PZ):
            H += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        H += field[i] * davies.site_op(PZ, i, n)
    w, v = np.linalg.eigh(H)
    e = np.exp(-beta * (w - w.min()))
    return (v * (e / e.sum())) @ v.conj().T


def weight_n_pauli(n):
    W = Ypauli
    for _ in range(n - 1):
        W = np.kron(W, Ypauli)
    return W


def marginal(rho, n, keep):
    perm = list(keep) + [q for q in range(n) if q not in keep]
    k = len(keep)
    t = rho.reshape([2] * (2 * n)).transpose(
        perm + [q + n for q in perm]).reshape(2 ** k, 2 ** (n - k),
                                              2 ** k, 2 ** (n - k))
    return np.einsum('ajbj->ab', t)


if __name__ == "__main__":
    rho = gibbs_state_beta(N, BETA, seed=N)
    W = weight_n_pauli(N)
    lam_min = float(np.linalg.eigvalsh(rho).min())
    c = 0.8 * lam_min
    rho_bad = rho + c * W
    assert np.linalg.eigvalsh(rho_bad).min() > -1e-12

    worst = max(float(np.abs(marginal(rho, N, keep)
                             - marginal(rho_bad, N, keep)).max())
                for k in (2, 3) for keep in combinations(range(N), k))
    tdist = 0.5 * float(np.abs(np.linalg.eigvalsh(rho_bad - rho)).sum())
    purity_gap = float(np.real(np.trace(rho_bad @ rho_bad)
                               - np.trace(rho @ rho)))

    w_signal = float(np.real(np.trace(rho_bad @ W)))
    print(f"n = {N}, beta = {BETA}: rho_bad = Gibbs + {c:.5f} * "
          f"Y^(x{N})\n")
    print(f"max marginal diff (k<=3):   {worst:.2e}   "
          f"(any marginal-based fit is blind)")
    print(f"trace distance:             {tdist:.4f}   "
          f"(the misspecification is macroscopic)")
    print(f"<W> if you KNOW the frame:  {w_signal:.4f}   "
          f"(a product measurement - cheap for anyone)")
    print(f"frame UNKNOWN: single-copy auditor searches ~4^n = {4**N} "
          f"global Paulis;")
    print("two-copy Bell-difference sampling draws from the Pauli")
    print("spectrum directly and flags the deviation's support without")
    print("knowing the frame (purity-swap alone is weak here: gap "
          f"{purity_gap:.1e}).")
    print("\nLearning succeeds and lies; certification against hidden-")
    print("frame misspecification is the memory task. Candidate:")
    print("'certified agnostic tomography' of physical families + the")
    print("single-copy certification lower bound (shares the hidden-frame")
    print("core with L6 - likely the same theorem).")
