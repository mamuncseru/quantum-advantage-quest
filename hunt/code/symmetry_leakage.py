"""L7 first numerics: does symmetry-class breaking leak into low-weight
observables of quench data?

Task family (QUALM/HCP-flavored, physical version): decide whether the
dynamics generating the lab's quench ensemble is time-reversal symmetric
(real local H) or not (complex local H), from copies of
|psi(t)> = exp(-iHt)|+...+> at uniformly random times.

L7's collapse conjecture: for LOCAL H the class leaks into low-weight
observables of the time-averaged state - odd-Y Pauli expectations vanish
for the real class (rho-bar is a real matrix) and are generically Omega(1)
for the complex class. If true, single-copy shadows decide the class in
poly time and the exponential symmetry-testing advantage collapses on
physical data; the residue is globally-hidden symmetry breaking (L6's
shield again).

Run: .venv/bin/python hunt/code/symmetry_leakage.py
"""

from itertools import combinations

import numpy as np

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1.0, -1.0]).astype(complex)
I2 = np.eye(2, dtype=complex)
N = 6


def site_op(P, i, n):
    op = np.array([[1.0]], dtype=complex)
    for q in range(n):
        op = np.kron(op, P if q == i else I2)
    return op


def local_hamiltonian(n, rng, complex_class):
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        H += rng.normal() * site_op(X, i, n) @ site_op(X, i + 1, n)
        H += rng.normal() * site_op(Z, i, n) @ site_op(Z, i + 1, n)
        if complex_class:
            # XY-type term: real coefficient, IMAGINARY matrix elements
            H += rng.normal() * site_op(X, i, n) @ site_op(Y, i + 1, n)
    for i in range(n):
        H += rng.normal() * site_op(Z, i, n)
    return H


def dephased_state(H, n):
    """EXACT infinite-time average of the quench ensemble: the dephased
    state sum_k |c_k|^2 |v_k><v_k| - real matrix iff H (and psi0) real.
    This is the class invariant; finite-time grids converge to it at the
    dephasing rate (slowly at small n - computed exactly here instead)."""
    w, v = np.linalg.eigh(H)
    psi0 = np.ones(2 ** n, dtype=complex) / 2 ** (n / 2)
    c2 = np.abs(v.conj().T @ psi0) ** 2
    return (v * c2) @ v.conj().T


def max_low_weight_odd_y(rho, n, k=2):
    """max |Tr rho P| over Paulis of weight <= k with an odd number of Ys."""
    paulis = {'X': X, 'Y': Y, 'Z': Z}
    best = 0.0
    for w in (1, 2):
        for sites in combinations(range(n), w):
            for labels in np.ndindex(*([3] * w)):
                names = ['XYZ'[l] for l in labels]
                if names.count('Y') % 2 == 0:
                    continue
                P = np.array([[1.0]], dtype=complex)
                for q in range(n):
                    P = np.kron(P, paulis[names[sites.index(q)]]
                                if q in sites else I2)
                best = max(best, abs(float(np.real(np.trace(P @ rho)))))
    return best


if __name__ == "__main__":
    print(f"max low-weight odd-Y expectation of the DEPHASED quench "
          f"state (n={N}, exact)\n")
    print(f"{'class':>9} {'seed':>5} {'leakage':>11}")
    for complex_class in (False, True):
        for seed in range(3):
            H = local_hamiltonian(N, np.random.default_rng(seed),
                                  complex_class)
            leak = max_low_weight_odd_y(dephased_state(H, N), N)
            print(f"{'complex' if complex_class else 'real':>9} "
                  f"{seed:>5} {leak:>11.2e}")
    print("\nReal class: exactly 0 (real eigenvectors); complex class:")
    print("Omega(1) - the symmetry class leaks into 2-local observables")
    print("of the dephased ensemble, so single-copy shadows decide it in")
    print("poly time. The HCP-type advantage collapses on local quench")
    print("data; residue = globally hidden breaking (the L6 shield).")
    print("Caveat: finite-time grids converge only at the dephasing rate;")
    print("the experimental protocol needs late/random times.")
