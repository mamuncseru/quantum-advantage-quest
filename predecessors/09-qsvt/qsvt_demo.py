"""Qubitization / QSVT (Low-Chuang 2016, Gilyen-Su-Low-Wiebe 2019) —
the grand unification, in its smallest honest demo.

Block-encode a Hermitian A (||A|| < 1) into the walk operator

    W = [[A, B], [-B, A]],   B = sqrt(I - A^2)

On each eigenvector of A with eigenvalue lambda = cos(theta), W acts on a
2D invariant subspace as a rotation by theta. Hence

    top-left block of W^d  =  T_d(A)      (Chebyshev polynomial of A)

One unitary, applied d times, implements a degree-d polynomial of the
encoded matrix. QSP phases between applications extend this from Chebyshev
polynomials to (essentially) arbitrary bounded polynomials — sign function
gives search, 1/x gives linear systems, e^{-ix} gives simulation.
"""

import numpy as np


def random_hermitian(dim, norm=0.9, seed=0):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    A = (M + M.conj().T) / 2
    return A * (norm / np.linalg.norm(A, 2))


def walk_operator(A):
    lam, V = np.linalg.eigh(A)
    B = (V * np.sqrt(1 - lam ** 2)) @ V.conj().T
    return np.block([[A, B], [-B, A]])


def chebyshev_of_matrix(A, d):
    lam, V = np.linalg.eigh(A)
    return (V * np.cos(d * np.arccos(lam))) @ V.conj().T


def top_left_block(W, dim):
    return W[:dim, :dim]


if __name__ == "__main__":
    dim = 8
    A = random_hermitian(dim)
    W = walk_operator(A)
    print("W unitary:", np.allclose(W @ W.conj().T, np.eye(2 * dim)))
    Wd = np.eye(2 * dim)
    for d in range(1, 7):
        Wd = Wd @ W
        err = np.linalg.norm(top_left_block(Wd, dim) - chebyshev_of_matrix(A, d), 2)
        print(f"  d = {d}: || (W^d)_00 - T_d(A) || = {err:.2e}")
