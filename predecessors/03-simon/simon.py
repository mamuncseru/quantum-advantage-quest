"""Simon (1994) — the first big-AND-robust separation, and Shor's trigger.

f: {0,1}^n -> {0,1}^n hides s != 0 via f(x) = f(x XOR s), 2-to-1.
Each quantum run of the H-sandwich yields a uniformly random y with y.s = 0;
n-1 independent y's + Gaussian elimination over GF(2) recover s.
Classical: Omega(2^(n/2)) queries (birthday bound). Quantum: O(n).
"""

import numpy as np

from qsim import H, apply, sample, zero_state


def function_oracle(f, n_in, n_out):
    """|x>|y> -> |x>|y XOR f(x)>; x on qubits 0..n_in-1, y on the rest."""
    N = 2 ** (n_in + n_out)
    U = np.zeros((N, N), dtype=complex)
    for x in range(2 ** n_in):
        fx = f(x)
        for y in range(2 ** n_out):
            U[(x << n_out) | (y ^ fx), (x << n_out) | y] = 1.0
    return U


def make_simon_function(s, n, rng):
    """Random 2-to-1 function with f(x) = f(x XOR s); s != 0."""
    assert 0 < s < 2 ** n
    values = rng.permutation(2 ** n)
    table, label, next_label = {}, {}, 0
    for x in range(2 ** n):
        rep = min(x, x ^ s)
        if rep not in label:
            label[rep] = int(values[next_label])
            next_label += 1
        table[x] = label[rep]
    return lambda x: table[x]


def rref_nullspace(rows, n):
    """rows: ints, independent, rank n-1. Return the nonzero s (as int) with
    y.s = 0 mod 2 for all y. Null space of a rank-(n-1) system is {0, s}."""
    A = np.array([[(y >> (n - 1 - i)) & 1 for i in range(n)] for y in rows],
                 dtype=int)
    m = A.shape[0]
    pivot_cols, r = [], 0
    for c in range(n):
        hits = np.nonzero(A[r:, c])[0]
        if hits.size == 0:
            continue
        A[[r, r + hits[0]]] = A[[r + hits[0], r]]
        for i in range(m):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        pivot_cols.append(c)
        r += 1
        if r == m:
            break
    free = [c for c in range(n) if c not in pivot_cols]
    assert len(free) == 1, "need rank exactly n-1"
    s_bits = np.zeros(n, dtype=int)
    s_bits[free[0]] = 1
    for row, c in enumerate(pivot_cols):
        s_bits[c] = A[row, free[0]]
    return int("".join(map(str, s_bits)), 2)


def simon(f, n, seed=None, max_samples=None):
    """Recover s. Returns (s, number_of_quantum_queries_worth_of_samples)."""
    oracle = function_oracle(f, n, n)
    psi = zero_state(2 * n)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, oracle, list(range(2 * n)))
    for q in range(n):
        psi = apply(psi, H, [q])
    # Sampling the final state repeatedly = statistics of independent runs
    # (one query each); the honest query count is the number of samples used.
    max_samples = max_samples or 20 * n
    shots = sample(psi, shots=max_samples, qubits=range(n), seed=seed)

    basis, independent = [], []
    used = 0
    for bits in shots:
        used += 1
        y = int(bits, 2)
        z = y
        for b in basis:                      # reduce by current basis
            z = min(z, z ^ b)
        if z:
            basis.append(z)
            independent.append(y)
        if len(independent) == n - 1:
            break
    else:
        raise RuntimeError("not enough independent equations; increase samples")

    s = rref_nullspace(independent, n)
    for x in (0, 1, 3, 7):                   # verify the promise was used right
        assert f(x % 2 ** n) == f((x % 2 ** n) ^ s)
    return s, used


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 5
    s_true = 0b10110
    f = make_simon_function(s_true, n, rng)
    s, queries = simon(f, n, seed=7)
    print(f"n = {n}, hidden s = {s_true:0{n}b}")
    print(f"recovered s = {s:0{n}b} using {queries} quantum queries")
    print(f"classical lower bound is Omega(2^(n/2)) ~ {int(2**(n/2))} queries;"
          f" at n = 60 that is ~10^9 vs ~{20*60} quantum.")
