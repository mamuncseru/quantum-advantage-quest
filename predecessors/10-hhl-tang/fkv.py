"""Tang 2018 / FKV sketch — feel, in code, how an advantage dies.

HHL-style quantum ML promised exponential speedups for low-rank linear
algebra, assuming quantum state preparation access to the data. Tang's
observation: the honest classical analogue of that assumption is
l2-SAMPLING access — and with it, classical algorithms (built on the
Frieze-Kannan-Vempala sketch below) match the quantum ones up to
polynomial factors. The advantage was never quantum; it lived in the
access assumption.

Here: approximate the top-k row space of a big low-rank matrix from a few
l2-sampled rows, and compare against the true best rank-k approximation.
"""

import numpy as np


def make_low_rank(m, n, k, noise=0.01, seed=0):
    rng = np.random.default_rng(seed)
    U = np.linalg.qr(rng.normal(size=(m, k)))[0]
    V = np.linalg.qr(rng.normal(size=(n, k)))[0]
    s = np.linspace(10, 2, k)
    return U @ np.diag(s) @ V.T + noise * rng.normal(size=(m, n)) / np.sqrt(n)


def fkv_row_space(A, k, r, seed=0):
    """Approximate top-k right singular vectors from r l2-sampled rows.

    Sampling rows with p_i ~ ||A_i||^2 and rescaling by 1/sqrt(r p_i) gives a
    small matrix S with E[S^T S] = A^T A — so S's right singular vectors
    approximate A's. THIS is the step quantum state preparation was secretly
    doing for free.
    """
    rng = np.random.default_rng(seed)
    p = (A ** 2).sum(axis=1)
    p = p / p.sum()
    idx = rng.choice(A.shape[0], size=r, p=p)
    S = A[idx] / np.sqrt(r * p[idx, None])
    return np.linalg.svd(S, full_matrices=False)[2][:k]      # (k, n)


def reconstruction_ratio(A, k, r, seed=0):
    """||A - A P_fkv||_F / ||A - A_k||_F ; 1.0 would be optimal."""
    Vk = fkv_row_space(A, k, r, seed)
    err_fkv = np.linalg.norm(A - A @ Vk.T @ Vk, "fro")
    s = np.linalg.svd(A, compute_uv=False)
    err_best = np.sqrt((s[k:] ** 2).sum())
    return err_fkv / err_best


if __name__ == "__main__":
    m = n = 1500
    k = 5
    A = make_low_rank(m, n, k)
    print(f"A: {m} x {n}, rank ~{k} + noise. Best-vs-FKV reconstruction:")
    for r in (25, 50, 100, 200, 400):
        ratio = reconstruction_ratio(A, k, r)
        print(f"  r = {r:4d} sampled rows ({100*r/m:4.1f}% of A):"
              f" error ratio = {ratio:6.3f}")
    print("A handful of sampled rows ~ matches the optimal rank-k projection.")
    print("The 'exponential' quantum advantage was the access model, not physics.")
