"""Hamiltonian simulation via Trotterization (Lloyd 1996) — Feynman's program.

H = A + B with [A, B] != 0; e^{-iHt} != e^{-iAt} e^{-iBt}, but splitting time
into n slices converges: first order errs as O(t^2/n), the symmetric
(Strang) second order as O(t^3/n^2). We measure both slopes empirically on a
transverse-field Ising chain.
"""

import numpy as np
from scipy.linalg import expm

from qsim import I2, X, Z


def kron_chain(ops):
    M = np.array([[1.0 + 0j]])
    for op in ops:
        M = np.kron(M, op)
    return M


def tfim(n, g=1.0):
    """H = -sum Z_i Z_{i+1} - g sum X_i, split into (ZZ part, X part)."""
    dim_ops = lambda op, i: kron_chain([op if j == i else I2 for j in range(n)])
    A = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        A -= kron_chain([Z if j in (i, i + 1) else I2 for j in range(n)])
    B = np.zeros_like(A)
    for i in range(n):
        B -= g * dim_ops(X, i)
    return A, B


def trotter_error(A, B, t, n_steps, order):
    U_exact = expm(-1j * (A + B) * t)
    dt = t / n_steps
    if order == 1:
        step = expm(-1j * A * dt) @ expm(-1j * B * dt)
    elif order == 2:
        step = expm(-1j * A * dt / 2) @ expm(-1j * B * dt) @ expm(-1j * A * dt / 2)
    else:
        raise ValueError(order)
    return np.linalg.norm(np.linalg.matrix_power(step, n_steps) - U_exact, 2)


def measured_slope(order, n_qubits=6, t=1.0, steps=(4, 8, 16, 32, 64)):
    """Fit error ~ n^slope on a log-log plot; expect ~ -order."""
    A, B = tfim(n_qubits)
    errs = [trotter_error(A, B, t, n, order) for n in steps]
    slope = np.polyfit(np.log(steps), np.log(errs), 1)[0]
    return slope, errs


if __name__ == "__main__":
    for order in (1, 2):
        slope, errs = measured_slope(order)
        print(f"order {order}: errors {['%.2e' % e for e in errs]}")
        print(f"          fitted slope = {slope:+.2f} (theory: {-order})")
