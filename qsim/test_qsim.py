import numpy as np
import pytest

from qsim import (CNOT, H, X, Z, amplitudes, apply, bitflip_oracle,
                  controlled, phase_oracle, probabilities, sample, zero_state)


def kron_1q(U, q, n):
    """Reference: full 2^n matrix for a single-qubit gate on qubit q."""
    M = np.array([[1.0 + 0j]])
    for i in range(n):
        M = np.kron(M, U if i == q else np.eye(2))
    return M


def full_matrix(U, qubits, n):
    """Reference: full 2^n matrix for a k-qubit gate, built entry by entry."""
    N, k = 2 ** n, len(qubits)
    M = np.zeros((N, N), dtype=complex)
    for col in range(N):
        bits = [(col >> (n - 1 - q)) & 1 for q in range(n)]
        sub_in = int("".join(str(bits[q]) for q in qubits), 2)
        for sub_out in range(2 ** k):
            if U[sub_out, sub_in] == 0:
                continue
            nb = bits.copy()
            for j, q in enumerate(qubits):
                nb[q] = (sub_out >> (k - 1 - j)) & 1
            row = int("".join(map(str, nb)), 2)
            M[row, col] += U[sub_out, sub_in]
    return M


def random_unitary(dim, rng):
    A = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    Q, _ = np.linalg.qr(A)
    return Q


def test_zero_state():
    psi = zero_state(3)
    a = amplitudes(psi)
    assert a[0] == 1.0 and np.allclose(np.linalg.norm(a), 1.0)


def test_bell_state():
    psi = zero_state(2)
    psi = apply(psi, H, [0])
    psi = apply(psi, CNOT, [0, 1])
    assert np.allclose(amplitudes(psi),
                       [1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])


def test_ghz_sampling():
    psi = zero_state(3)
    psi = apply(psi, H, [0])
    psi = apply(psi, CNOT, [0, 1])
    psi = apply(psi, CNOT, [1, 2])
    shots = sample(psi, shots=2000, seed=1)
    assert set(shots) == {"000", "111"}
    frac = shots.count("000") / len(shots)
    assert 0.42 < frac < 0.58


def test_single_qubit_gate_matches_kron_reference():
    rng = np.random.default_rng(7)
    n = 4
    psi0 = rng.normal(size=(2,) * n) + 1j * rng.normal(size=(2,) * n)
    psi0 /= np.linalg.norm(psi0)
    for q in range(n):
        U = random_unitary(2, rng)
        got = amplitudes(apply(psi0, U, [q]))
        want = kron_1q(U, q, n) @ amplitudes(psi0)
        assert np.allclose(got, want)


def test_two_qubit_gate_on_nonadjacent_reversed_qubits():
    rng = np.random.default_rng(11)
    n = 4
    psi0 = rng.normal(size=(2,) * n) + 1j * rng.normal(size=(2,) * n)
    psi0 /= np.linalg.norm(psi0)
    for qubits in ([0, 1], [2, 0], [3, 1], [1, 3]):
        U = random_unitary(4, rng)
        got = amplitudes(apply(psi0, U, qubits))
        want = full_matrix(U, qubits, n) @ amplitudes(psi0)
        assert np.allclose(got, want)


def test_controlled_builds_cnot():
    assert np.allclose(controlled(X), CNOT)


def test_phase_kickback_ties_the_two_oracle_forms():
    """|x>|-> under the bitflip oracle == phase-oracle result, tensor |->."""
    n = 3
    f = lambda x: bin(x).count("1") & 1  # parity
    psi = zero_state(n + 1)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, X, [n])
    psi = apply(psi, H, [n])           # ancilla -> |->
    kicked = apply(psi, bitflip_oracle(f, n), list(range(n + 1)))

    ref = zero_state(n)
    for q in range(n):
        ref = apply(ref, H, [q])
    ref = apply(ref, phase_oracle(f, n), list(range(n)))
    minus = np.array([1, -1]) / np.sqrt(2)
    want = np.tensordot(ref, minus, axes=0)
    assert np.allclose(kicked, want)


def test_unitarity_roundtrip():
    rng = np.random.default_rng(3)
    n = 5
    psi0 = rng.normal(size=(2,) * n) + 1j * rng.normal(size=(2,) * n)
    psi0 /= np.linalg.norm(psi0)
    U = random_unitary(4, rng)
    psi = apply(apply(psi0, U, [1, 3]), U.conj().T, [1, 3])
    assert np.allclose(psi, psi0)


def test_probabilities_normalized():
    psi = apply(zero_state(2), H, [0])
    p = probabilities(psi)
    assert np.isclose(p.sum(), 1.0)
