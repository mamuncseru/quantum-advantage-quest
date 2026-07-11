"""L6 first numerics: the marginal-blindness shield, and where it leaks.

Cross-platform comparison of physical states collapses when states are
marginal-parameterized (AAKS). The shield candidates are sector pairs
that are LOCALLY IDENTICAL: here the minimal instance, |GHZ+-> on n
qubits. Exact facts demonstrated:

  1. every (n-1)-qubit marginal of the two sectors is IDENTICAL;
  2. a frame-KNOWN global product measurement (X-string parity) still
     distinguishes them in one shot - marginal-blindness is not
     single-copy-blindness;
  3. under a hidden product-Clifford frame the distinguishing string
     becomes one unknown weight-n Pauli among ~4^n, while the
     frame-free two-copy overlap test is unaffected.

So the honest L6 window is: hidden-frame sector pairs - which is
stabilizer-structure finding (L4's machinery) on the single-copy side.

Run: .venv/bin/python hunt/code/ghz_shield.py
"""

import numpy as np

N = 8


def ghz_pair(n):
    plus = np.zeros(2 ** n, dtype=complex)
    minus = np.zeros(2 ** n, dtype=complex)
    plus[0] = plus[-1] = 1 / np.sqrt(2)
    minus[0], minus[-1] = 1 / np.sqrt(2), -1 / np.sqrt(2)
    return plus, minus


def marginal_without(psi, n, drop):
    """(n-1)-qubit marginal after tracing out qubit `drop`."""
    perm = [q for q in range(n) if q != drop] + [drop]
    t = psi.reshape([2] * n).transpose(perm).reshape(2 ** (n - 1), 2)
    return t @ t.conj().T


def random_product_clifford(n, rng):
    """Random single-qubit Clifford-ish frame (Haar 1q suffices here)."""
    us = []
    for _ in range(n):
        z = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        q, _ = np.linalg.qr(z)
        us.append(q)
    U = us[0]
    for u in us[1:]:
        U = np.kron(U, u)
    return U


if __name__ == "__main__":
    psi_p, psi_m = ghz_pair(N)

    worst = max(
        float(np.abs(marginal_without(psi_p, N, d)
                     - marginal_without(psi_m, N, d)).max())
        for d in range(N))
    print(f"n = {N} GHZ sector pair")
    print(f"1. max entry-diff over all (n-1)-marginals: {worst:.2e}")

    Xs = np.array([[0, 1], [1, 0]], dtype=complex)
    Xn = Xs
    for _ in range(N - 1):
        Xn = np.kron(Xn, Xs)
    print(f"2. frame-known X-string parity: <+|X..X|+> = "
          f"{np.real(np.vdot(psi_p, Xn @ psi_p)):+.3f}, "
          f"<-|X..X|-> = {np.real(np.vdot(psi_m, Xn @ psi_m)):+.3f}"
          f"   (one-shot separation)")

    rng = np.random.default_rng(6)
    U = random_product_clifford(N, rng)
    fp, fm = U @ psi_p, U @ psi_m
    worst_f = max(
        float(np.abs(marginal_without(fp, N, d)
                     - marginal_without(fm, N, d)).max())
        for d in range(N))
    xstr = np.real(np.vdot(fp, Xn @ fp)) - np.real(np.vdot(fm, Xn @ fm))
    print(f"3. hidden frame: marginal diff still {worst_f:.2e}; "
          f"old X-string signal now {abs(xstr):.3f};")
    print(f"   frame-free overlap |<f+|f->|^2 = "
          f"{abs(np.vdot(fp, fm))**2:.2e}  (two-copy swap sees "
          f"orthogonality regardless)")
    print("\nWindow: hidden-frame sector pairs. Single-copy must find one")
    print("weight-n string among ~4^n; two-copy comparison is frame-free.")
    print("Finding the frame IS stabilizer-structure learning (L4).")
