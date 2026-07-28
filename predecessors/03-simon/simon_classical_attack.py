"""The attack on the oracle every Simon demonstration actually uses.

Simon's exponential separation is a statement about a BLACK BOX. To run
the algorithm on hardware you must build the box out of gates, and the
construction everyone reaches for is a LINEAR function

    f(x) = A x   over GF(2),  with  ker A = {0, s}

because a linear map is nothing but a network of CNOTs — cheap, shallow,
and exactly what a device can execute.

The catch: a linear f is classically trivial. Query the n unit vectors,
read off the columns of A, compute its kernel. That is n queries, no
collisions, no birthday bound -- the same order as the quantum algorithm.
The exponential separation is GONE, and it was the oracle, not the
hardware, that gave it away.

This file measures both halves of that claim:

  1. break_linear()   -- recovers s from a linear oracle in exactly n
                         classical queries;
  2. birthday_hunt()  -- against a genuinely random 2-to-1 table, the
                         same attacker is reduced to collision hunting,
                         and the query count grows like 2^(n/2).

Run:  .venv/bin/python predecessors/03-simon/simon_classical_attack.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from simon import make_simon_function  # noqa: E402


# ---------------------------------------------------------------- linear --

def linear_simon_oracle(s, n):
    """f(x) = x XOR (x_p . s) where p is any set bit of s.

    Linear, 2-to-1, and ker = {0, s}:  f(s) = s XOR s = 0, and f(x) = 0
    forces x in {0, s}. As a circuit it is pure CNOT — see
    simon_on_hardware.py, which runs exactly this map on noisy machines.
    """
    assert 0 < s < 2 ** n
    p = (s & -s).bit_length() - 1          # lowest set bit of s
    return lambda x: x ^ (s if (x >> p) & 1 else 0)


def break_linear(f, n):
    """Recover s from a LINEAR oracle using n queries and linear algebra.

    Query the unit vectors to get the matrix columns, then find the
    unique non-zero kernel vector by Gaussian elimination over GF(2).
    """
    cols = [f(1 << i) for i in range(n)]   # the n queries, and that is all
    # A[r][c] = bit r of the image of e_c
    A = [[(cols[c] >> r) & 1 for c in range(n)] for r in range(n)]
    piv, where = 0, []
    for c in range(n):
        r = next((r for r in range(piv, n) if A[r][c]), None)
        if r is None:
            continue
        A[piv], A[r] = A[r], A[piv]
        for r2 in range(n):
            if r2 != piv and A[r2][c]:
                A[r2] = [a ^ b for a, b in zip(A[r2], A[piv])]
        where.append(c)
        piv += 1
    free = [c for c in range(n) if c not in where]
    assert len(free) == 1, "kernel must be one-dimensional"
    fc = free[0]
    s_bits = [0] * n
    s_bits[fc] = 1
    for row, c in enumerate(where):
        s_bits[c] = A[row][fc]
    s = 0
    for i in range(n):
        s |= s_bits[i] << i
    return s, len(cols)


# -------------------------------------------------------------- birthday --

def birthday_hunt(f, n, rng, cap=None):
    """The only classical route against an unstructured 2-to-1 f: sample
    until two inputs collide. Returns (s, queries)."""
    cap = cap or 40 * 2 ** (n // 2 + 2)
    seen = {}
    for q in range(1, cap + 1):
        x = int(rng.integers(0, 2 ** n))
        v = f(x)
        if v in seen and seen[v] != x:
            return seen[v] ^ x, q
        seen[v] = x
    return None, cap


if __name__ == "__main__":
    print("1. the linear oracle — the one hardware demos build\n")
    print(f"   {'n':>3}{'classical queries':>20}{'s recovered':>14}")
    for n in (4, 6, 8, 12, 16, 20):
        s_true = (1 << (n - 1)) | 0b1011
        f = linear_simon_oracle(s_true, n)
        s, q = break_linear(f, n)
        print(f"   {n:>3}{q:>20}{('yes' if s == s_true else 'NO'):>14}")
    print("\n   n queries, deterministic, no collisions needed."
          "\n   The quantum algorithm also costs O(n). No separation at all.")

    print("\n2. a genuinely random 2-to-1 table — the real Simon promise\n")
    print(f"   {'n':>3}{'median classical queries':>26}{'2^(n/2)':>12}")
    rng = np.random.default_rng(11)
    for n in (4, 6, 8, 10, 12, 14):
        qs = []
        for t in range(21):
            f = make_simon_function(
                int(rng.integers(1, 2 ** n)), n, np.random.default_rng(t))
            _, q = birthday_hunt(f, n, rng)
            qs.append(q)
        print(f"   {n:>3}{int(np.median(qs)):>26}{2 ** (n / 2):>12.0f}")
    print("\n   Here the attacker really is stuck at the birthday bound,"
          "\n   and Simon's exponential separation is real.")
    print("\nMoral: the separation lives in the PROMISE, not the circuit."
          "\nAn oracle you can build cheaply is usually an oracle you can"
          "\nbreak cheaply — which is what makes instantiation the whole"
          "\ngame (see notes.md section 6).")
