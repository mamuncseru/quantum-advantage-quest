"""L10 first numerics (doubles as L2's pre-registered T-scaling probe):
does the temporal-memory Fisher edge GROW with the number of steps?

QUALM (Aharonov-Cotler-Qi) proves coherent access to dynamics is
exponentially stronger than incoherent access on adversarial ensembles.
Physical version: the non-Markovian dyad of nonmarkov_fisher.py, now at
T = 2, 3, 4 steps. Protocol A re-prepares and measures every step
(classical memory across steps); protocol B stays coherent throughout
with one entangled ancilla, Bell measurement at the end. If the ratio
grows with T, temporal coherence compounds - the QUALM mechanism showing
up in a lab-shaped instance.

Run: .venv/bin/python hunt/code/qualm_scaling.py
"""

import sys
from itertools import product
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from nonmarkov_fisher import PAULI, _eig_basis, cfi, step_unitary  # noqa

I2 = np.eye(2, dtype=complex)


def protocol_A_dist_T(theta, basis, T):
    """T-step measure-and-reprepare in one Pauli basis; joint 2^T-outcome
    distribution."""
    U = step_unitary(theta)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho_plus = np.outer(plus, plus.conj())
    V = _eig_basis(PAULI[basis])
    branches = {(): (1.0, np.diag([1.0, 0.0]).astype(complex))}
    for _ in range(T):
        nxt = {}
        for hist, (p, rho_B) in branches.items():
            rho_SB = U @ np.kron(rho_plus, rho_B) @ U.conj().T
            for o in (0, 1):
                P = np.kron(np.outer(V[:, o], V[:, o].conj()), I2)
                blk = P @ rho_SB @ P
                po = float(np.real(np.trace(blk)))
                rb = (np.trace((blk / po).reshape(2, 2, 2, 2),
                               axis1=0, axis2=2)
                      if po > 1e-14 else np.eye(2, dtype=complex) / 2)
                nxt[hist + (o,)] = (p * po, rb)
        branches = nxt
    return np.array([p for p, _ in branches.values()])


def protocol_B_dist_T(theta, T):
    """S-A Bell pair kept coherent through T steps; Bell measurement."""
    U4 = step_unitary(theta).reshape(2, 2, 2, 2)
    psi = np.zeros((2, 2, 2), dtype=complex)
    psi[0, 0, 0] = psi[1, 0, 1] = 1 / np.sqrt(2)
    for _ in range(T):
        psi = np.einsum('SBsb,sba->SBa', U4, psi)
    probs = []
    for phase, flip in [(1, 0), (-1, 0), (1, 1), (-1, 1)]:
        v = np.zeros((2, 2), dtype=complex)
        v[0, flip] = 1 / np.sqrt(2)
        v[1, 1 - flip] = phase / np.sqrt(2)
        amp = np.einsum('sba,sa->b', psi, v.conj())
        probs.append(float(np.real(np.vdot(amp, amp))))
    return np.array(probs)


if __name__ == "__main__":
    print("Fisher information ratio (coherent / best incoherent) vs T\n")
    print(f"{'T':>3} {'best FI_A':>10} {'FI_B':>8} {'ratio':>7}")
    theta = 0.6
    for T in (2, 3, 4):
        fi_a = max(cfi(lambda t: protocol_A_dist_T(t, b, T), theta)
                   for b in 'XYZ')
        fi_b = cfi(lambda t: protocol_B_dist_T(t, T), theta)
        print(f"{T:>3} {fi_a:>10.4f} {fi_b:>8.4f} {fi_b/fi_a:>7.2f}")
    print("\nGrowth with T = temporal coherence compounding (the QUALM")
    print("mechanism in a lab-shaped instance); saturation = constant-")
    print("factor edge only (L2 kill-2 territory). Restricted protocol")
    print("classes; the comb-SDP version is the rigorous next step.")
