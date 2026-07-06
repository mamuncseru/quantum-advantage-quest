"""Deutsch-Jozsa (1992) on our own simulator — the worked example.

Read this against notes.md section 3. The whole algorithm is a Hadamard
sandwich around one phase-oracle application; the answer is read off the
amplitude that interference concentrates on |0...0>.
"""

import numpy as np

from qsim import H, amplitudes, apply, phase_oracle, zero_state


def dj_p0(oracle, n):
    """Probability of measuring |0...0> after the H-sandwich circuit.

    That amplitude equals 2^-n * sum_x (-1)^f(x) — the MEAN of (-1)^f,
    i.e. the Fourier coefficient of (-1)^f at 0. Constant f: +-1.
    Balanced f: exactly 0. One query reads a global property of f.
    """
    psi = zero_state(n)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, oracle, list(range(n)))
    for q in range(n):
        psi = apply(psi, H, [q])
    return abs(amplitudes(psi)[0]) ** 2


def deutsch_jozsa(oracle, n):
    """Decide constant vs balanced with ONE oracle application."""
    return "constant" if dj_p0(oracle, n) > 0.5 else "balanced"


if __name__ == "__main__":
    n = 10
    cases = {
        "f(x) = 0            ": lambda x: 0,
        "f(x) = 1            ": lambda x: 1,
        "f(x) = parity(x)    ": lambda x: bin(x).count("1") & 1,
        "f(x) = top bit of x ": lambda x: (x >> (n - 1)) & 1,
    }
    print(f"Deutsch-Jozsa, n = {n} qubits, one oracle query each:\n")
    for name, f in cases.items():
        oracle = phase_oracle(f, n)
        print(f"  {name} p0 = {dj_p0(oracle, n):6.4f} -> {deutsch_jozsa(oracle, n)}")

    # The promise is load-bearing: f = AND of the top two bits is neither
    # constant nor balanced (1/4 of inputs map to 1). p0 = 1/4, and the
    # algorithm's output is meaningless for this f.
    f_and = lambda x: ((x >> (n - 1)) & (x >> (n - 2))) & 1
    oracle = phase_oracle(f_and, n)
    print(f"\n  f(x) = AND(top 2 bits) — OUTSIDE the promise:")
    print(f"    p0 = {dj_p0(oracle, n):6.4f} -> "
          f"'{deutsch_jozsa(oracle, n)}' (meaningless: f is neither)")
