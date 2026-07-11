"""L2 suspect-1 first data: does quantum memory across time steps help
learn a non-Markovian bath coupling?

Smallest instance: system qubit S, hidden bath qubit B (persists across
steps), step unitary U(theta) = exp(-i theta (XX + YY)/4) on S-B, T = 2
steps. Task: estimate theta. Compare classical Fisher information per
2-step experiment:

  protocol A (no quantum memory): fresh probe |+> on S each step, measure
      S after each step in the best Pauli basis; classical memory across
      steps allowed (joint outcome statistics used).
  protocol B (quantum memory): S entangled with an idle ancilla A, kept
      COHERENT through both steps (no mid-measurement), Bell-basis
      measurement on S+A at the end.

Both protocol classes are restricted (fixed natural measurement families)
- this is an upper-bound comparison on a first instance, not a
separation proof; the honest deliverable is the FI ratio curve.

Run: .venv/bin/python hunt/code/nonmarkov_fisher.py
"""

import numpy as np

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1.0, -1.0]).astype(complex)
I2 = np.eye(2, dtype=complex)
PAULI = {'X': X, 'Y': Y, 'Z': Z}


def step_unitary(theta):
    H = (np.kron(X, X) + np.kron(Y, Y)) / 4
    w, v = np.linalg.eigh(H)
    return (v * np.exp(-1j * theta * w)) @ v.conj().T


def _eig_basis(P):
    w, v = np.linalg.eigh(P)
    return v[:, np.argsort(-w)]


def protocol_A_dist(theta, b1, b2):
    """Joint 4-outcome distribution: fresh |+> probes, measure S in Pauli
    basis b1 then b2; the bath persists between steps."""
    U = step_unitary(theta)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho_plus = np.outer(plus, plus.conj())
    V1, V2 = _eig_basis(PAULI[b1]), _eig_basis(PAULI[b2])
    rho1 = U @ np.kron(rho_plus, np.diag([1.0, 0.0])) @ U.conj().T
    probs = []
    for o1 in (0, 1):
        P1 = np.kron(np.outer(V1[:, o1], V1[:, o1].conj()), I2)
        blk = P1 @ rho1 @ P1
        p1 = float(np.real(np.trace(blk)))
        if p1 < 1e-15:
            probs += [0.0, 0.0]
            continue
        rho_B1 = np.trace((blk / p1).reshape(2, 2, 2, 2),
                          axis1=0, axis2=2)
        rho2 = U @ np.kron(rho_plus, rho_B1) @ U.conj().T
        for o2 in (0, 1):
            P2 = np.kron(np.outer(V2[:, o2], V2[:, o2].conj()), I2)
            probs.append(p1 * float(np.real(np.trace(P2 @ rho2))))
    return np.array(probs)


def protocol_B_dist(theta):
    """S-A Bell pair, S coherent through both steps, Bell measurement on
    S+A at the end. Qubit order (S, B, A)."""
    U4 = step_unitary(theta).reshape(2, 2, 2, 2)      # (S',B',S,B)
    psi = np.zeros((2, 2, 2), dtype=complex)          # (S, B, A)
    psi[0, 0, 0] = psi[1, 0, 1] = 1 / np.sqrt(2)
    psi = np.einsum('SBsb,sba->SBa', U4, psi)         # step 1
    psi = np.einsum('SBsb,sba->SBa', U4, psi)         # step 2
    probs = []
    for phase, flip in [(1, 0), (-1, 0), (1, 1), (-1, 1)]:
        v = np.zeros((2, 2), dtype=complex)           # Bell vector on (S,A)
        v[0, flip] = 1 / np.sqrt(2)
        v[1, 1 - flip] = phase / np.sqrt(2)
        amp = np.einsum('sba,sa->b', psi, v.conj())
        probs.append(float(np.real(np.vdot(amp, amp))))
    return np.array(probs)


def cfi(dist_fn, theta, d=1e-4):
    p = dist_fn(theta)
    dp = (dist_fn(theta + d) - dist_fn(theta - d)) / (2 * d)
    mask = p > 1e-12
    return float((dp[mask] ** 2 / p[mask]).sum())


if __name__ == "__main__":
    print("Fisher information per 2-step experiment, non-Markovian dyad\n")
    print(f"{'theta':>7} {'best FI_A (no memory)':>22} "
          f"{'FI_B (memory)':>14} {'ratio':>7}")
    for theta in (0.3, 0.6, 0.9, 1.2):
        fi_a = max(cfi(lambda t: protocol_A_dist(t, b1, b2), theta)
                   for b1 in 'XYZ' for b2 in 'XYZ')
        fi_b = cfi(protocol_B_dist, theta)
        print(f"{theta:>7.1f} {fi_a:>22.4f} {fi_b:>14.4f} "
              f"{fi_b / fi_a if fi_a > 1e-12 else float('inf'):>7.2f}")
    print("\nRestricted protocol classes on one instance - an existence")
    print("probe for suspect 1, not a separation proof. Ratio > 1 means")
    print("temporal quantum memory sees bath correlations that the best")
    print("measure-and-reprepare Pauli protocol misses here.")
