"""Shor (1994) on our simulator — the masterclass in problem-first thinking.

Two halves, and the genius is in the FIRST one:
  1. Classical reduction: factoring N -> finding the order r of a mod N.
  2. Quantum order finding: phase estimation of the modular-multiplication
     unitary; the QFT reads the period out of the phase.

Registers: t = 2m+1 counting qubits + m = ceil(log2(N+1)) work qubits.
"""

from fractions import Fraction
from math import ceil, gcd, log2

import numpy as np

from qsim import H, X, amplitudes, apply, controlled, sample, zero_state

SWAP = np.array([[1, 0, 0, 0],
                 [0, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1]], dtype=complex)


def R(k):
    """Phase gate diag(1, e^{2 pi i / 2^k})."""
    return np.diag([1.0, np.exp(2j * np.pi / 2 ** k)])


def qft(psi, qubits):
    """QFT on `qubits` (qubits[0] = most significant), Nielsen-Chuang circuit."""
    t = len(qubits)
    for i, q in enumerate(qubits):
        psi = apply(psi, H, [q])
        for k in range(2, t - i + 1):
            psi = apply(psi, controlled(R(k)), [qubits[i + k - 1], q])
    for i in range(t // 2):
        psi = apply(psi, SWAP, [qubits[i], qubits[t - 1 - i]])
    return psi


def qft_dagger(psi, qubits):
    """Inverse QFT: the qft circuit reversed, phases conjugated."""
    t = len(qubits)
    for i in range(t // 2):
        psi = apply(psi, SWAP, [qubits[i], qubits[t - 1 - i]])
    for i, q in reversed(list(enumerate(qubits))):
        for k in reversed(range(2, t - i + 1)):
            psi = apply(psi, controlled(R(k).conj()), [qubits[i + k - 1], q])
        psi = apply(psi, H, [q])
    return psi


def mod_mult_unitary(c, N, m):
    """Permutation |x> -> |c x mod N> for x < N (identity above N).
    A bijection on [0, N) exactly because gcd(c, N) = 1."""
    d = 2 ** m
    U = np.zeros((d, d), dtype=complex)
    for x in range(d):
        U[(c * x) % N if x < N else x, x] = 1.0
    return U


def order_finding_state(a, N):
    """Run the order-finding circuit; return (final state, t)."""
    m = ceil(log2(N + 1))
    t = 2 * m + 1
    work = list(range(t, t + m))
    psi = zero_state(t + m)
    for q in range(t):
        psi = apply(psi, H, [q])
    psi = apply(psi, X, [work[-1]])              # work register = |1>
    for j in range(t):
        # counting qubit j has weight 2^(t-1-j): controls U^(2^(t-1-j)).
        # pow() computes a^(2^(t-1-j)) mod N classically — repeated squaring
        # is O(t) multiplications; THIS is where the real circuit cost lives.
        power = pow(a, 2 ** (t - 1 - j), N)
        psi = apply(psi, controlled(mod_mult_unitary(power, N, m)), [j] + work)
    psi = qft_dagger(psi, list(range(t)))
    return psi, t


def find_order(a, N, shots=30, seed=0):
    """Order of a mod N via phase estimation + continued fractions."""
    psi, t = order_finding_state(a, N)
    # Repeated sampling of the fixed final state = independent circuit runs.
    for bits in sample(psi, shots=shots, qubits=range(t), seed=seed):
        c = int(bits, 2)
        if c == 0:
            continue
        r = Fraction(c, 2 ** t).limit_denominator(N).denominator
        for mult in range(1, 5):                 # gcd(k, r) > 1 fix-up
            if pow(a, r * mult, N) == 1:
                return r * mult
    return None


def shor_factor(N, seed=0):
    """Return a nontrivial factor pair of N (N odd, composite, not a prime power)."""
    rng = np.random.default_rng(seed)
    while True:
        a = int(rng.integers(2, N))
        g = gcd(a, N)
        if g > 1:
            continue                             # lucky gcd; take the quantum path
        r = find_order(a, N, seed=int(rng.integers(10**6)))
        if r is None or r % 2:
            continue
        x = pow(a, r // 2, N)
        if x == N - 1:
            continue
        f1, f2 = gcd(x - 1, N), gcd(x + 1, N)
        if 1 < f1 < N:
            return tuple(sorted((f1, N // f1))) + (a, r)
        if 1 < f2 < N:
            return tuple(sorted((f2, N // f2))) + (a, r)


if __name__ == "__main__":
    import time
    for N in (15, 21, 35):
        t0 = time.time()
        p, q, a, r = shor_factor(N, seed=1)
        print(f"N = {N:2d} = {p} x {q}   (a = {a:2d}, order r = {r:2d},"
              f" {ceil(log2(N+1))*3+1} qubits, {time.time()-t0:5.1f} s)")
