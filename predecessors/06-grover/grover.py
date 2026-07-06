"""Grover (1996) / amplitude amplification — the quadratic workhorse.

Rotation picture: the state lives in span{|w>, |rest>}; each iteration
(oracle + diffusion) rotates it by 2*arcsin(1/sqrt(N)) toward |w>.
Optimal iterations ~ (pi/4) sqrt(N); more is WORSE (overshoot).
BBBV: quadratic is a ceiling for unstructured search, not a floor.
"""

import numpy as np

from qsim import H, amplitudes, apply, phase_oracle, zero_state


def diffusion(n):
    """2|s><s| - I about the uniform state |s> = H^n |0>."""
    N = 2 ** n
    return 2.0 * np.full((N, N), 1.0 / N) - np.eye(N)


def grover(n, marked, iterations=None):
    """Search a single marked item; return (success_prob, iterations)."""
    N = 2 ** n
    if iterations is None:
        iterations = int(np.floor(np.pi / 4 * np.sqrt(N)))
    oracle = phase_oracle(lambda x: x == marked, n)
    D = diffusion(n)
    qubits = list(range(n))
    psi = zero_state(n)
    for q in qubits:
        psi = apply(psi, H, [q])
    for _ in range(iterations):
        psi = apply(psi, oracle, qubits)
        psi = apply(psi, D, qubits)
    return abs(amplitudes(psi)[marked]) ** 2, iterations


def success_curve(n, marked, k_max):
    """Success probability after k = 0..k_max iterations (exact, rotation picture
    verified against the circuit): sin^2((2k+1) theta), theta = arcsin(2^-n/2)."""
    theta = np.arcsin(2 ** (-n / 2))
    return [np.sin((2 * k + 1) * theta) ** 2 for k in range(k_max + 1)]


if __name__ == "__main__":
    n = 8
    marked = 137
    p, k = grover(n, marked)
    print(f"n = {n} (N = {2**n}), marked = {marked}")
    print(f"optimal k = {k}: success = {p:.4f} (classical: k/N = {k/2**n:.4f})")
    p2, k2 = grover(n, marked, iterations=2 * k)
    print(f"overshoot 2k = {k2}: success = {p2:.4f}  <- more queries, worse")
