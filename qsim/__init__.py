"""
qsim — hand-built statevector simulator (curriculum rule: no black boxes).

Conventions
-----------
- An n-qubit state is a complex numpy array of shape (2,)*n; qubit q is axis q.
- Flattened in C order (see `amplitudes`), the basis index reads as the
  big-endian bitstring b0 b1 ... b_{n-1}: qubit 0 is the most significant bit.
- A k-qubit gate is a (2^k, 2^k) matrix whose row/column index is the
  big-endian bitstring of the qubits it acts on: in `apply(psi, U, qubits)`,
  qubits[0] is the gate's most significant bit.
- Oracles here are dense 2^n matrices. Building one costs exponential
  classical time — the query model doesn't charge for that, and that is
  exactly its fine print (predecessors/01-deutsch-jozsa/notes.md, section 4).
"""

import numpy as np

# ---------------------------------------------------------------- gates ----

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
CNOT = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1],
                 [0, 0, 1, 0]], dtype=complex)


def controlled(U):
    """Controlled-U; the control qubit is the more significant index."""
    U = np.asarray(U, dtype=complex)
    d = U.shape[0]
    M = np.eye(2 * d, dtype=complex)
    M[d:, d:] = U
    return M


# ---------------------------------------------------------------- state ----

def zero_state(n):
    """|0...0> on n qubits."""
    psi = np.zeros((2,) * n, dtype=complex)
    psi[(0,) * n] = 1.0
    return psi


def amplitudes(psi):
    """Flat amplitude vector; index = big-endian bitstring of qubits 0..n-1."""
    return psi.reshape(-1)


def probabilities(psi):
    p = np.abs(amplitudes(psi)) ** 2
    return p / p.sum()


def apply(psi, U, qubits):
    """Apply a k-qubit gate U (2^k x 2^k) to `qubits`; returns a new state.

    U is reshaped to (2,)*2k: the first k axes are outputs, the last k inputs.
    tensordot contracts the input axes against the state's qubit axes, then
    moveaxis puts the k output axes back where the qubits live.
    """
    n = psi.ndim
    k = len(qubits)
    U = np.asarray(U, dtype=complex).reshape((2,) * (2 * k))
    psi = np.tensordot(U, psi, axes=(list(range(k, 2 * k)), list(qubits)))
    return np.moveaxis(psi, range(k), qubits)


def sample(psi, shots=1, qubits=None, seed=None):
    """Measure all qubits `shots` times; report bits of `qubits` (default all).

    Returns a list of bitstrings, qubits in the order given.
    """
    rng = np.random.default_rng(seed)
    n = psi.ndim
    p = probabilities(psi)
    idx = rng.choice(p.size, size=shots, p=p)
    if qubits is None:
        qubits = range(n)
    return ["".join("1" if (i >> (n - 1 - q)) & 1 else "0" for q in qubits)
            for i in idx]


# -------------------------------------------------------------- oracles ----

def bitflip_oracle(f, n):
    """(n+1)-qubit unitary |x>|y> -> |x>|y XOR f(x)>.

    Qubits 0..n-1 are the input register, qubit n the target.
    """
    N = 2 ** (n + 1)
    U = np.zeros((N, N), dtype=complex)
    for x in range(2 ** n):
        fx = f(x) & 1
        for y in (0, 1):
            U[(x << 1) | (y ^ fx), (x << 1) | y] = 1.0
    return U


def phase_oracle(f, n):
    """n-qubit diagonal unitary |x> -> (-1)^f(x) |x>."""
    return np.diag([(-1.0) ** (f(x) & 1) for x in range(2 ** n)]).astype(complex)
